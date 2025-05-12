from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=4, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefresh(BaseModel):
    refresh_token: str