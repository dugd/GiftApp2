import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app as _app
from app.core.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_session():
    async with TestSessionLocal() as session:
        yield session

_app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="session")
async def async_client():
    async with engine.begin() as conn:
        from app.models.base import Base
        import app.api.v1.features.models # noqa
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(
            transport=ASGITransport(app=_app),
            base_url="http://test"
    ) as client:
        yield client
