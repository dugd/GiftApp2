from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.core.enums import MediaType


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


class MediaFileModel(MediaFileBase):
    id: UUID



class MediaFileRead(MediaFileBase):
    id: UUID


class MediaFileShort(BaseModel):
    id: UUID
    url: HttpUrl
    alt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)