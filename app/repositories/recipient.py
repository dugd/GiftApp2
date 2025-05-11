from uuid import UUID
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipient
from app.repositories.orm import SQLAlchemyRepository


class RecipientRepository(SQLAlchemyRepository[Recipient]):
    def __init__(self, session: AsyncSession):
        super().__init__(Recipient, session)

    async def get_by_user_id(self, user_id: UUID) -> List[Recipient]:
        stmt = select(Recipient).where(self._model.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
