from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict

from app.core.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole


class UserModel(UserBase):
    id: UUID
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)



class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
