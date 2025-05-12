from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from jose import ExpiredSignatureError, JWTError

from app.core.enums import TokenType
from app.exceptions.auth import UserAlreadyActivated
import app.service.auth as auth_service
import app.service.user as user_service
from app.mail import SendgridMailSender
from app.repositories.orm.user import UserRepository
from app.schemas.auth import UserRegister, TokenPair
from app.schemas.user import UserRead, UserModel
from app.api.v1.dependencies import DBSessionDepends, CurrentRootUser, CurrentSimpleUser, get_access_token_payload
from app.utils.security import decode_token
from .dependencies import refresh_token_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(db: DBSessionDepends, user_data: UserRegister):
    user = await auth_service.register_user(user_data, UserRepository(db), SendgridMailSender())
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
        db: DBSessionDepends,
        token: str,
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
        user = await auth_service.activate_user(UUID(user_id), UserRepository(db))
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
async def login(db: DBSessionDepends, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.authenticate_user(form_data.username, form_data.password, UserRepository(db))
    response = auth_service.create_token_pair(user)
    return response


@router.post("/refresh", response_model=TokenPair)
async def refresh(db: DBSessionDepends, token_payload: dict = Depends(refresh_token_scheme)):
    if not token_payload or "id" not in token_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await user_service.get_user_by_id(token_payload["id"], UserRepository(db))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    response = auth_service.create_token_pair(user)
    return response


@router.get("/me")
async def me(payload: dict = Depends(get_access_token_payload)):
    return payload
