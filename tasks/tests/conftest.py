from asgi_lifespan import LifespanManager
import logging.config
import pytest
import pytest_asyncio
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from api.settings import get_settings
from api.models.base import Base
import httpx
from api.logs import LOGGING_CONFIG
# Import app after toggling test mode
from api.main import app  # noqa: E402
from api.deps.rabbit_conn import get_channel  # noqa: E402

# Configure logging first
logging.config.dictConfig(LOGGING_CONFIG)

# Ensure external service connections are disabled for unit tests
os.environ.setdefault("DISABLE_EXTERNAL_SERVICES", "1")

cfg = get_settings()
engine = create_async_engine(cfg.POSTGRES_URL_ASYNC, echo=True)
TestingSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False)


@pytest.fixture(scope="session")
def settings():
    """Fixture to provide settings for tests"""
    return get_settings()

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Database Fixture
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Creates test database and drops tables after tests.
    Skips when external services are disabled.
    """
    if os.getenv("DISABLE_EXTERNAL_SERVICES") == "1":
        yield
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create tables
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Cleanup

@pytest.fixture()
async def db_session():
    """Provides an async database session"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()  # Rollback after each test

@pytest.fixture
async def api():
    # app.dependency_overrides[get_database] = get_test_database
    async with LifespanManager(app) as manager:
        yield manager.app

@pytest_asyncio.fixture
async def test_client(api):
    transport = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://app.io", timeout=30
    ) as client:
        yield client

# ---- RabbitMQ dependency overrides ----

class _DummyExchange:
    async def publish(self, *args, **kwargs):
        return None


class _DummyChannel:
    async def declare_exchange(self, *args, **kwargs):
        return _DummyExchange()

    async def close(self):
        return None


@pytest.fixture(scope="session")
def dummy_rabbit_channel():
    return _DummyChannel()


@pytest.fixture(autouse=True)
def override_rabbit_dependency(dummy_rabbit_channel):
    """Provide a dummy rabbit channel in all tests to avoid real connections."""
    app.dependency_overrides[get_channel] = lambda: dummy_rabbit_channel
    yield
    app.dependency_overrides.pop(get_channel, None)

@pytest.fixture()
def dummy_workflow():
    return [
        {
            'action': 'http_request',
            "params": {
                "url": 'https://jsonplaceholder.typicode.com/users/1',
            },
        },
        {
            'action': 'summarize_text',
            "params": None
        },
        {
            'action': 'save_to_database',
            "params": None
        },
    ]

# Override FastAPI Dependency
# @pytest.fixture()
# async def test_app_client(db_session):
#     """Override FastAPI dependencies for testing"""
#     from fastapi.testclient import TestClient
#     from app.dependencies import get_db  # Import your dependency

#     async def override_get_db():
#         yield db_session

#     app.dependency_overrides[get_db] = override_get_db
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()  # Reset dependencies after test


# engine = create_engine(
#     "sqlite:///:memory:",
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )
# Base.metadata.create_all(bind=engine)  # Bind the engine

# from sqlalchemy.orm import sessionmaker
# TestingSessionLocal = sessionmaker(
#     autocommit=False, autoflush=False, bind=engine
# )
# @pytest.fixture
# def test_db_session():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
