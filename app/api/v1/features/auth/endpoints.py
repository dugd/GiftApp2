from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.core.database import get_session
from app.api.v1.dependencies import get_current_user
from app.api.v1.features.auth.dependencies import refresh_token_scheme
from app.api.v1.features.auth.schemas import UserRegister, UserRead, TokenPair
from app.api.v1.features.auth.service import get_user_by_id, register_user, authenticate_user, create_token_pair

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_session)):
    user = await register_user(user_data, db)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    response = create_token_pair(user)
    return response


@router.post("/refresh", response_model=TokenPair)
async def refresh(token_payload: dict = Depends(refresh_token_scheme), db: AsyncSession = Depends(get_session)):
    if not token_payload or "id" not in token_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await get_user_by_id(token_payload["id"], db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    response = create_token_pair(user)

    return response


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
