from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.repositories.orm.user import UserRepository
from app.schemas.user import UserModel
from app.service.user import get_user_by_id
from app.exceptions.exceptions import NotFoundError
from app.api.v1.features.auth.dependencies import access_token_scheme


async def get_session():
    async with async_session() as session:
        yield session


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
        token_payload: dict = Depends(get_token_payload)) -> UserModel:
    try:
        user = await get_user_by_id(token_payload["id"], UserRepository(db))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return user


class RoleChecker:
    def __init__(self, *allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserModel = Depends(get_current_user)) -> bool:
        if not user.role in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return True


DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDepends = Annotated[UserModel, Depends(get_current_user)]