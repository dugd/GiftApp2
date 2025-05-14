from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.repositories.orm import UserRepository
from app.service.user import UserService


async def get_session():
    async with async_session() as session:
        yield session


DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]


async def get_user_service(db: DBSessionDepends):
    return UserService(UserRepository(db))