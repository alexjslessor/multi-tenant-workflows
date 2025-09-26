import logging
from collections.abc import AsyncGenerator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models.base import Base
from .settings import get_settings


settings = get_settings()
logger = logging.getLogger('uvicorn')
engine_async = create_async_engine(settings.POSTGRES_URL_ASYNC)
async_session_maker = async_sessionmaker(engine_async, expire_on_commit=False)

# Synchronous engine/session for background workers (e.g., Celery)
engine_sync = create_engine(
    settings.POSTGRES_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

async def create_all_tables():
    async with engine_async.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations.

    This is intended for use in worker processes (Celery) where
    async sessions are cumbersome. It ensures commit/rollback/close.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()