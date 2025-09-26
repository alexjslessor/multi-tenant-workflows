import pytest
import asyncio
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from api.routers.postgres_routes import Base, get_db, engine
from api.main import app


@pytest.fixture(scope='session', autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope='session', autouse=False)
def event_loop():
    try:
        loop = asyncio.get_running_loop()
        asyncio.set_event_loop(loop)
    except RuntimeError as e:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception as e:
        raise Exception(f"Error event_loop: {e!s}")
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def api():
    async with LifespanManager(app) as manager:
        yield manager.app

@pytest_asyncio.fixture
async def test_client(api):
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://app.io") as client:
        yield client