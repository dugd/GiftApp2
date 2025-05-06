from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def add(self, user: User) -> User:
        self.db.add(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)

    async def commit(self):
        await self.db.commit()
