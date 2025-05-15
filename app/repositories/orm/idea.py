from uuid import UUID
from typing import List, Any, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.orm.base import SQLAlchemyRepository
from app.models.idea import GiftIdea


class IdeaRepository(SQLAlchemyRepository[GiftIdea]):
    def __init__(self, session: AsyncSession):
        super().__init__(GiftIdea, session)

    def _base_stmt(self) -> Select:
        return select(GiftIdea).where(GiftIdea.deleted_at == None)

    async def get_by_user_id(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            desc_order: bool = False,
            **filters: Any,
    ) -> List[GiftIdea]:
        return await self.list(
            skip=skip,
            limit=limit,
            order_by=order_by,
            desc_order=desc_order,
            user_id=user_id, **filters
        )