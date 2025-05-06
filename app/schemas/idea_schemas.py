from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, AnyUrl


class IdeaBase(BaseModel):
    title: str = Field(min_length=2)
    tags: Optional[List[str]] = Field(default=None)
    description: Optional[str] = None
    view_url: Optional[AnyUrl] = None
    estimated_price: Optional[Decimal] = None
    is_global: bool = None


class IdeaCreate(IdeaBase):
    pass


class IdeaModel(IdeaBase):
    id: UUID

    user_id: Optional[UUID] = None

    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IdeaUpdateInfo(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2)
    tags: Optional[List[str]] = Field(default=None)
    description: Optional[str] = None
    view_url: Optional[AnyUrl] = None
    estimated_price: Optional[Decimal] = None