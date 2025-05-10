from typing import List, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import MediaFile


class MediaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, media: MediaFile) -> MediaFile:
        self.db.add(media)
        await self.db.commit()
        return media

    async def add_many(self, media: List[MediaFile]) -> List[MediaFile]:
        self.db.add_all(media)
        await self.db.commit()
        return media

    async def delete(self, media: MediaFile) -> None:
        await self.db.delete(media)
        await self.db.commit()

    async def update(self, media: MediaFile, data: dict) -> MediaFile:
        for key, value in data.items():
            setattr(media, key, value)
        await self.db.commit()
        return media

    async def get_by_id(self, media_id: UUID) -> MediaFile | None:
        stmt = select(MediaFile).where(MediaFile.id == media_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hash(self, media_hash: str) -> MediaFile:
        stmt = select(MediaFile).where(MediaFile.hash == media_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[MediaFile]:
        result = await self.db.execute(select(MediaFile))
        return result.scalars().all()
