from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.database import async_session
from app.exceptions.auth import UserIsNotActivated
from app.schemas.user import UserModel
from app.service.user import UserService
from app.exceptions.common import NotFoundError
from .security import access_token_scheme


async def get_session():
    async with async_session() as session:
        yield session


async def get_access_token_payload(
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
        user_service: UserService = Depends(get_user_service),
        token_payload: dict = Depends(get_access_token_payload)) -> UserModel:
    try:
        user = await user_service.get_user_by_id(token_payload["id"])
        if not user.is_active:
            raise UserIsNotActivated(user.username)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return user


class RoleChecker:
    def __init__(self, *allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserModel = Depends(get_current_user)) -> UserModel:
        if not user.role in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return user


get_current_simple_user = RoleChecker(UserRole.USER.value)
get_current_admin_user  = RoleChecker(UserRole.ADMIN.value, UserRole.ROOT.value)
get_current_root_user   = RoleChecker(UserRole.ROOT.value)


DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDepends = Annotated[UserModel, Depends(get_current_user)]
CurrentSimpleUser = Annotated[UserModel, Depends(get_current_simple_user)]
CurrentAdminUser  = Annotated[UserModel, Depends(get_current_admin_user)]
CurrentRootUser   = Annotated[UserModel, Depends(get_current_root_user)]