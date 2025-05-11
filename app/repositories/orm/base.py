from typing import Type, Any, Optional, List, Dict

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.abstract.base import AbstractRepository, T


class SQLAlchemyRepository(AbstractRepository[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self._session = session
        self._model = model

    async def add(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.commit()
        return entity

    async def update(self, entity: T, data: Dict[str, Any]) -> T:
        for field, value in data.items():
            setattr(entity, field, value)
        await self._session.flush()
        await self._session.commit()
        return entity

    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        await self._session.flush()
        await self._session.commit()

    async def list(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            desc_order: bool = False,
            **filters: Any,
        ) -> List[T]:
        stmt = select(self._model)

        for attr, value in filters.items():
            column = getattr(self._model, attr, None)
            if column is None:
                continue
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)

        if order_by:
            column = getattr(self._model, order_by, None)
            if column is not None:
                if desc_order:
                    stmt = stmt.order_by(desc(column))
                else:
                    stmt = stmt.order_by(column)


        stmt = stmt.offset(skip)
        if limit > 0:
            stmt = stmt.limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, _id: Any) -> Optional[T]:
        stmt = select(self._model).where(self._model.id == _id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(self, _id: Any) -> bool:
        stmt = select(self._model).where(self._model.id == _id)
        result = await self._session.execute(stmt)
        return bool(result.first())

    async def count(self) -> int:
        stmt = select(func.count(self._model))
        result = await self._session.execute(stmt)
        return result.first()[0]
