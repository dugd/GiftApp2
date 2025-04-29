from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.auth.models import User
from app.api.v1.features.auth.schemas import UserRegister, UserRead, TokenPair
from app.api.v1.features.auth.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token
)
from app.api.v1.features.auth.dependencies import get_current_user, refresh_token_scheme
from app.core.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=str(user_data.email), hashed_password=hash_password(user_data.password))
    db.add(user)
    await db.commit()

    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    new_access_token = create_access_token(
        payload={"id": user.id, "sub": user.email, "role": user.role, "type": "access"})
    new_refresh_token = create_refresh_token(payload={"id": user.id, "type": "refresh"})

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh(token_payload: dict = Depends(refresh_token_scheme), db: AsyncSession = Depends(get_session)):
    if not token_payload or "id" not in token_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    query = select(User).where(User.id == token_payload["id"])
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access_token = create_access_token(
        payload={"id": user.id, "sub": user.email, "role": user.role, "type": "access"})
    new_refresh_token = create_refresh_token(payload={"id": user.id, "type": "refresh"})

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
