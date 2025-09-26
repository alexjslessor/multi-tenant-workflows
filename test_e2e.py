import os
import requests
import logging

logger = logging.getLogger(__name__)

def test_keycloak_client_credentials_token():
    """Authenticate to the local Keycloak via client credentials flow.
    Uses defaults from docker-compose.override.yml and allows overrides via env:
    - KEYCLOAK_TOKEN_URL
    - KEYCLOAK_CLIENT_ID
    - KEYCLOAK_SECRET
    """
    token_url = os.getenv(
        "KEYCLOAK_TOKEN_URL",
        "http://localhost:8080/realms/demo-mcp/protocol/openid-connect/token",
    )
    client_id = os.getenv("KEYCLOAK_CLIENT_ID", "mcp-secure")
    client_secret = os.getenv("KEYCLOAK_SECRET", "6UJzbvU6H29BeiiEUx6f4lfqKFzMu9nD")

    resp = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=10,
    )

    assert resp.status_code == 200, f"Unexpected status {resp.status_code}: {resp.text}"
    payload = resp.json()
    logger.info(payload)
    print(payload)

    # Basic assertions on token response
    assert payload.get("token_type", "").lower() == "bearer"
    assert payload.get("access_token"), "Missing access_token in response"
    assert isinstance(payload.get("expires_in"), int)
    return payload