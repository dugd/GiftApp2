from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

import app.service.auth as auth_service
import app.service.user as user_service
from app.schemas.auth import UserRegister, TokenPair
from app.schemas.user import UserModel
from app.api.v1.dependencies import CurrentUserDepends, DBSessionDepends
from app.api.v1.features.auth.dependencies import refresh_token_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def register(db: DBSessionDepends, user_data: UserRegister):
    user = await auth_service.register_user(user_data, db)
    return user


@router.post("/login", response_model=TokenPair)
async def login(db: DBSessionDepends, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.authenticate_user(form_data.username, form_data.password, db)
    response = auth_service.create_token_pair(user)
    return response


@router.post("/refresh", response_model=TokenPair)
async def refresh(db: DBSessionDepends, token_payload: dict = Depends(refresh_token_scheme)):
    if not token_payload or "id" not in token_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await user_service.get_user_by_id(token_payload["id"], db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    response = auth_service.create_token_pair(user)
    return response


@router.get("/me", response_model=UserModel)
async def me(current_user: CurrentUserDepends):
    return current_user
