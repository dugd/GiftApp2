from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict

from app.core.enums import UserRole
from app.schemas.media import MediaFileShort

class UserBase(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    display_name: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserModel(UserBase):
    avatar: Optional[MediaFileShort] = None
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
