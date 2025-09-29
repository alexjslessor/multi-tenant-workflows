from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TITLE: str = 'Workflows API'
    PREFIX: str = ''
    DOCS_URL: str = '/docs'
    OPENAPI_URL: str = '/openapi'
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']
    CORS_ORIGINS: list[str] = ['*']
    RABBIT: str
    REDIS_URL: str
    POSTGRES_URL: str
    OPENAI_API_KEY: str = 'sk-Rt7ipOp_1dw2LePgJ6NZc1bii2PqH6tcQ1msGVkvryT3BlbkFJkQ9NVAHcahNbjxjs755swPpM-yysYANh3ZuePHSx4A'

    @property
    def POSTGRES_URL_ASYNC(self) -> str:
        return self.POSTGRES_URL.replace('postgresql://', 'postgresql+asyncpg://')

@lru_cache()
def get_settings() -> BaseSettings:
    try:
        return Settings()
    except Exception as e:
        raise