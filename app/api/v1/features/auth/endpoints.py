from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.auth.models import User
from app.api.v1.features.auth.schemas import UserRegister, UserRead, TokenPair, TokenRefresh
from app.api.v1.features.auth.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.core.database import get_session

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
bearer_scheme = HTTPBearer()

async def get_current_user(db: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    async with db.begin():
        query = select(User).where(User.email == payload["sub"])
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


@router.post("/register")
async def register(user_data: UserRegister = Depends(), session: AsyncSession = Depends(get_session())):
    async with session.begin():
        query = select(User).where(User.email == user_data.email)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = User(email=str(user_data.email), hashed_password=hash_password(user_data.password))

    return UserRead.model_validate(user)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session())):
    async with db.begin():
        query = select(User).where(User.email == form_data.username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token = create_access_token(payload={"id": user.id, "sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(payload={"id": user.id})

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(token_in: TokenRefresh, db: AsyncSession = Depends(get_session)):
    payload = decode_token(token_in.refresh_token)
    if not payload or "id" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    async with db.begin():
        query = select(User).where(User.id == payload["id"])
        result = await db.execute(query)
        user = result.scalar_one_or_none()

    new_access_token = create_access_token(payload={"id": user.id, "sub": user.email, "role": user.role})
    new_refresh_token = create_refresh_token(payload={"id": user.id})

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
