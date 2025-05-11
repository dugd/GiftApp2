from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.orm.base import SQLAlchemyRepository
from app.models.media import MediaFile


class MediaRepository(SQLAlchemyRepository[MediaFile]):
    def __init__(self, session: AsyncSession):
        super().__init__(MediaFile, session)

    async def add_many(self, media: List[MediaFile]) -> List[MediaFile]:
        self._session.add_all(media)
        await self._session.flush()
        await self._session.commit()
        return media

    async def get_by_hash(self, media_hash: str) -> MediaFile:
        stmt = select(self._model).where(self._model.hash == media_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
