from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.auth import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserRead(UserBase):
    id: UUID

    model_config =ConfigDict(from_attributes=True)
