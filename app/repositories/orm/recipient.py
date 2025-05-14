from uuid import UUID
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipient
from app.repositories.orm.base import SQLAlchemyRepository


class RecipientRepository(SQLAlchemyRepository[Recipient]):
    def __init__(self, session: AsyncSession):
        self._model = Recipient
        super().__init__(Recipient, session)

    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Recipient]:
        return await self.list(skip=skip, limit=limit, user_id=user_id)
