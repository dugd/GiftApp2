from uuid import UUID

from app.repositories.orm.user import UserRepository
from app.exceptions.common import NotFoundError
from app.schemas.user import UserBase


async def get_user_by_id(_id: UUID, repo: UserRepository) -> UserBase:
    user = await repo.get_by_id(_id)
    if not user:
        raise NotFoundError("User")
    return UserBase.model_validate(user)


async def get_user_by_email(email: str, repo: UserRepository) -> UserBase:
    user = await repo.get_by_email(email)
    if not user:
        raise NotFoundError("User")
    return UserBase.model_validate(user)
