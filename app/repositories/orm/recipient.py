from uuid import UUID
from typing import List, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipient
from app.repositories.orm.base import SQLAlchemyRepository


class RecipientRepository(SQLAlchemyRepository[Recipient]):
    def __init__(self, session: AsyncSession):
        super().__init__(Recipient, session)

    async def get_by_user_id(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            desc_order: bool = False,
            **filters: Any,
    ) -> List[Recipient]:
        return await self.list(
            skip=skip,
            limit=limit,
            order_by=order_by,
            desc_order=desc_order,
            user_id=user_id, **filters
        )
