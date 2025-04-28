from pydantic import BaseModel, EmailStr

from app.api.v1.features.auth.models import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class UserRead(UserBase):
    id: int

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str