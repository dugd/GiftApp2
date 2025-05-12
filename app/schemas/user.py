from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict

from app.core.enums import UserRole


class UserBase(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    ava_id: Optional[UUID] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserModel(UserBase):
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class UserRead(UserBase):
    pass
