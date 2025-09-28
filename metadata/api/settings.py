from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TITLE: str = 'Metadata API'
    PREFIX: str = ""
    ALGORITHM: str = "HS256"
    AUDIENCE: str = "aud-var"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    LIFETIME_SECONDS: int = 3600
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']
    SECRET: str
    DBNAME: str = 'users'
    postgres_url: str
    RABBIT: str

    @property
    def DOCS_URL(self) -> str:
        return f'{self.PREFIX}/docs'

    @property
    def OPENAPI_URL(self) -> str:
        return f'{self.PREFIX}/openapi'

    @property
    def POSTGRES_URL_ASYNC(self) -> str:
        return self.postgres_url.replace('postgresql://', 'postgresql+asyncpg://')

@lru_cache()
def get_settings() -> BaseSettings:
    try:
        return Settings()
    except KeyError as e:
        raise Exception(f'Env variable unset: {e}') from e
    except Exception as e:
        raise Exception(f'{e}') from e