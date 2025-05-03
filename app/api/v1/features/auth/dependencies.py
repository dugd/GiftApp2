from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.api.v1.features.auth.models import User
from app.api.v1.features.auth.security import decode_token
from app.api.v1.features.auth.service import get_user_by_id


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)

        token = creds.credentials

        try:
            token_data = decode_token(token)
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        self.verify_token_data(token_data)

        return token_data


    def verify_token_data(self, token_data):
        raise NotImplementedError("Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
access_token_scheme = AccessTokenBearer()
refresh_token_scheme = RefreshTokenBearer()


async def get_token_payload(
    token_payload: dict = Depends(access_token_scheme),
) -> dict:
    if "id" not in token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return token_payload


async def get_current_user(
        db: AsyncSession = Depends(get_session),
        token_payload: dict = Depends(get_token_payload)) -> User:
    async with db.begin():
        user = await get_user_by_id(token_payload["id"], db)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


class RoleChecker:
    def __init__(self, *allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> bool:
        if not user.role in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return True