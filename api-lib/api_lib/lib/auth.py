import jwt
import pytz
import time
import httpx
import logging
import datetime
from typing import Any
from fastapi import HTTPException, status, Request
from pydantic import BaseModel
from uuid import UUID

logger = logging.getLogger(__name__)

class Principal(BaseModel):
    sub: str
    tenant_id: UUID
    roles: list[str]

class JWKSCache:
    def __init__(self, jwks_url: str, ttl_seconds: int = 600):
        self._jwks_url = jwks_url
        self._ttl = ttl_seconds
        self._jwks: dict[str, Any] = {}
        self._fetched_at = 0.0

    async def get(self) -> dict[str, Any]:
        now = time.time()
        if not self._jwks or (now - self._fetched_at) > self._ttl:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self._jwks_url)
                resp.raise_for_status()
                self._jwks = resp.json()
                self._fetched_at = now
        return self._jwks

    async def get_key_by_kid(self, kid: str) -> dict[str, Any]:
        jwks = await self.get()
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        raise KeyError(f"JWK with kid={kid} not found")

class KeycloakVerifier:
    """
    FastAPI dependency class that verifies a Keycloak JWT and returns a Principal.
    Internal helpers are implemented as underscore-prefixed methods. The instance
    is callable (async) so it can be used directly with Depends().
    """
    def __init__(
        self,
        *,
        jwks_url: str,
        audience: str,
        issuer: str,
        jwks_cache_ttl: int = 600,
    ):
        self._audience = audience
        self._issuer = issuer
        self._jwks_cache = JWKSCache(jwks_url, ttl_seconds=jwks_cache_ttl)

    @staticmethod
    def _extract_bearer_token(
        authz: str | None,
    ) -> str:
        if not authz or not authz.lower().startswith("bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Missing or invalid Authorization header",
            )
        return authz.split(" ", 1)[1].strip()

    @staticmethod
    def _collect_roles(claims: dict[str, Any]) -> list[str]:
        roles: list[str] = []

        realm_roles = claims.get("realm_access", {}).get("roles", [])
        if isinstance(realm_roles, list):
            roles.extend(realm_roles)

        resource_access = claims.get("resource_access", {})
        for _client, data in resource_access.items():
            cr = data.get("roles", [])
            if isinstance(cr, list):
                roles.extend(cr)

        return sorted(set(roles))

    async def __call__(self, request: Request) -> Principal:
        token = self._extract_bearer_token(request.headers.get("Authorization"))

        try:
            header = jwt.get_unverified_header(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token kid")

        try:
            jwk = await self._jwks_cache.get_key_by_kid(kid)
        except KeyError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key")

        try:
            claims = jwt.decode(
                token,
                jwk,
                algorithms=[jwk.get("alg", "RS256")],
                audience=self._audience,
                issuer=str(self._issuer),
                options={
                    "verify_aud": True,
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                },
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token verification failed: {str(e)}")

        sub = claims.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing sub")

        tenant_id_raw = claims.get("tenant_id")
        if not tenant_id_raw:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant_id in token")
        try:
            tenant_id = UUID(str(tenant_id_raw))
        except Exception:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid tenant_id")

        roles = self._collect_roles(claims)
        return Principal(sub=sub, tenant_id=tenant_id, roles=roles)

def decode_jwt(
    secret: str, 
    token: str, 
    audience: str,
    algorithms: list[str] = ['HS256'],
    verify_signature: bool = False,
):
    """
    Args:
        secret (str): secret used for decryption
        token (str): jwt token
        audience (str): token audience
        algorithms (list[str], optional): Defaults to ['HS256'].
        verify_signature (bool, optional): Defaults to False.
    """
    try:
        payload = jwt.decode(
            token, 
            secret, 
            algorithms=algorithms,
            audience=audience,
            options={
                "verify_signature": verify_signature,
            },
        )

        exp = payload.get("exp", None)
        if exp:
            est_tz = pytz.timezone("America/New_York")  # Eastern Time Zone (EST/EDT)
            est = datetime.datetime.fromtimestamp(exp, datetime.timezone.utc).astimezone(est_tz)
            print(f"Token expiration time (EST/EDT): {est}")
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.error(f"Token has expired: {e}")
        raise Exception(f"Token has expired: {e}")
    except jwt.InvalidAudienceError as e:
        logger.error(f"Invalid audience: {e}")
        raise Exception(f"Invalid audience: {e}")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise Exception(f"Invalid token: {e}")
    except jwt.InvalidIssuerError as e:
        logger.error("Invalid issuer")
        raise Exception(f"Invalid issuer: {e}")
    except jwt.DecodeError:
        logger.error("Invalid token format")
        raise Exception(f"Invalid token format: {e}")
    except jwt.MissingRequiredClaimError as e:
        logger.error(f"Missing required claim: {e}")
        raise Exception(f"Missing Claim: {e}")