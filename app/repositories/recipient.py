from uuid import UUID
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Recipient


class RecipientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, recipient_id: UUID) -> Recipient | None:
        stmt = select(Recipient).where(Recipient.id == recipient_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[Recipient]:
        result = await self.db.execute(select(Recipient))
        return result.scalars().all()

    async def get_by_user_id(self, user_id: UUID) -> Sequence[Recipient]:
        stmt = select(Recipient).where(Recipient.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add(self, recipient: Recipient) -> Recipient:
        self.db.add(recipient)
        await self.db.commit()
        return recipient

    async def delete(self, recipient: Recipient) -> None:
        await self.db.delete(recipient)
        await self.db.commit()

    async def update(self, recipient: Recipient, data: dict) -> Recipient:
        for key, value in data.items():
            setattr(recipient, key, value)
        await self.db.commit()
        return recipient

    async def commit(self):
        await self.db.commit()
