from typing import Type, Any, Optional, List, Dict

from sqlalchemy import select, func
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

    async def list(self) -> List[T]:
        stmt = select(self._model)
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
