from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import User
from app.service.user import get_user_by_id
from app.api.v1.features.auth.dependencies import access_token_scheme


async def get_token_payload(
    token_payload: dict = Depends(access_token_scheme),
) -> dict:
    if "id" not in token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    token_payload["id"] = UUID(token_payload["id"])
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


DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDepends = Annotated[User, Depends(get_current_user)]