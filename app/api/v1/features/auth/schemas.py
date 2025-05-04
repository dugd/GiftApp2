from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models.auth import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserRead(UserBase):
    id: int

    model_config =ConfigDict(from_attributes=True)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str