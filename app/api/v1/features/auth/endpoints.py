from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from jose import ExpiredSignatureError, JWTError

from app.core.enums import TokenType
from app.exceptions.auth import UserAlreadyActivated
from app.service.auth import AuthService, UserRegistrationService
from app.service.user import UserService
from app.schemas.auth import UserRegister, TokenPair
from app.schemas.user import UserRead
from app.utils.security import decode_token
from app.api.v1.dependencies import CurrentRootUser, get_access_token_payload, refresh_token_scheme
from .dependencies import get_auth_service, get_register_service, get_user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserRegister,
        register_service: UserRegistrationService = Depends(get_register_service),
):
    user = await register_service.register(user_data)
    return {"msg": "Check your email to activate account"}


@router.post(
    "/register-admin",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_admin(user: CurrentRootUser):
    ...


@router.post("/register/activate")
async def confirm(
        token: str,
        auth_service: AuthService = Depends(get_auth_service),
):
    try:
        try:
            token_data = decode_token(token)
            if token_data["type"] != TokenType.activation.value:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = token_data["id"]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired activation token")
    try:
        await auth_service.activate_user(UUID(user_id))
    except UserAlreadyActivated:
        raise HTTPException(status_code=400, detail="Account already activated")

    return {"msg": "Account successfully activated"}


@router.post("/reset-password")
async def reset_password():
    ...


@router.post("/reset-password/confirm")
async def confirm_reset():
    ...


@router.post("/login", response_model=TokenPair)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    response = auth_service.create_token_pair(user)
    return response


@router.post("/refresh", response_model=TokenPair)
async def refresh(
        user_service: UserService = Depends(get_user_service),
        auth_service: AuthService = Depends(get_auth_service),
        token_payload: dict = Depends(refresh_token_scheme),
):
    if not token_payload or "id" not in token_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await user_service.get_user_by_id(token_payload["id"])
    response = auth_service.create_token_pair(user)

    return response


@router.get("/me")
async def me(payload: dict = Depends(get_access_token_payload)):
    return payload
