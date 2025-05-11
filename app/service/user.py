from uuid import UUID

from app.repositories.orm.user import UserRepository
from app.exceptions.exceptions import NotFoundError
from app.schemas.user import UserModel


async def get_user_by_id(_id: UUID, repo: UserRepository) -> UserModel:
    user = await repo.get_by_id(_id)
    if not user:
        raise NotFoundError("User")
    return UserModel.model_validate(user)


async def get_user_by_email(email: str, repo: UserRepository) -> UserModel:
    user = await repo.get_by_email(email)
    if not user:
        raise NotFoundError("User")
    return UserModel.model_validate(user)
