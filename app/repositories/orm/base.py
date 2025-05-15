from typing import TypeVar, Type, Any, Optional, List, Dict

from sqlalchemy import select, func, desc, ColumnElement, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.mixins import SurrogatePKMixin
from app.repositories.abstract.base import AbstractRepository


U = TypeVar("U", bound=SurrogatePKMixin)


class SQLAlchemyRepository(AbstractRepository[U]):
    def __init__(self, model: Type[U], session: AsyncSession):
        self._session = session
        self._model = model

    def _base_stmt(self) -> Select:
        return select(self._model)

    async def add(self, entity: U) -> U:
        self._session.add(entity)
        await self._session.flush()
        await self._session.commit()
        return entity

    async def update(self, entity: U, data: Dict[str, Any]) -> U:
        for field, value in data.items():
            setattr(entity, field, value)
        await self._session.flush()
        await self._session.commit()
        return entity

    async def delete(self, entity: U) -> None:
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
        ) -> List[U]:
        stmt = self._base_stmt()

        for attr, value in filters.items():
            strict = True
            if "__icontains" in attr:
                attr = attr.replace("__icontains", "")
                strict = False
            column: ColumnElement = getattr(self._model, attr, None)
            if column is None:
                continue
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value if strict else column.ilike(f"%{value}%"))

        if order_by:
            column = getattr(self._model, order_by, None)
            if column is not None:
                if desc_order:
                    stmt = stmt.order_by(desc(column))
                else:
                    stmt = stmt.order_by(column)

        if limit > 0:
            stmt = stmt.limit(limit)
        if skip > 0:
            stmt = stmt.offset(skip)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, _id: Any) -> Optional[U]:
        stmt = self._base_stmt().where(self._model.id == _id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(self, _id: Any) -> bool:
        stmt = self._base_stmt().where(self._model.id == _id)
        result = await self._session.execute(stmt)
        return bool(result.first())

    async def count(self) -> int:
        base_sub = self._base_stmt().subquery()
        stmt = select(func.count()).select_from(base_sub)
        result = await self._session.execute(stmt)
        return result.first()[0]
