from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app as _app
from app.core.models.base import Base
import app.models  # noqa
from app.models.auth import RootUser, SimpleUser
from app.api.v1.features.auth.security import hash_password
from app.core.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(db_session):
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(table.delete())
    await db_session.commit()


@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    async def _override_get_session() -> AsyncGenerator[AsyncSession, Any]:
        async with TestSessionLocal() as session:
            yield session

    _app.dependency_overrides[get_session] = _override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=_app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def root_user_token_headers(async_client, db_session) -> dict[str, str]:
    root_data = {
        "username": "root@example.com",
        "password": "12345678",
    }
    root_user = RootUser(
        email=root_data["username"],
        hashed_password=hash_password(root_data["password"]),
    )
    db_session.add(root_user)
    await db_session.commit()

    r = await async_client.post(f"api/v1/auth/login", data=root_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture(scope="function")
async def simple_user_token_headers(async_client, db_session) -> dict[str, str]:

    user_data = {
        "username": "user@example.com",
        "password": "12345678",
    }
    simple_user = SimpleUser(
        email=user_data["username"],
        hashed_password=hash_password(user_data["password"]),
    )
    db_session.add(simple_user)
    await db_session.commit()

    r = await async_client.post(f"api/v1/auth/login", data=user_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers