from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.models import MediaType


class MediaFileMeta(BaseModel):
    filename: str
    mime_type: str
    size_bytes: int
    width: int
    height: int
    ratio: float
    hash: str


class MediaFileBase(BaseModel):
    url: HttpUrl
    hash: str
    type: MediaType
    alt: Optional[str] = None
    mime_type: str
    width: int
    height: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MediaFileRead(MediaFileBase):
    id: UUID


class MediaFileModel(MediaFileBase):
    id: UUID
