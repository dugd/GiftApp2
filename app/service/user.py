from uuid import UUID

from app.repositories.orm.user import UserRepository
from app.exceptions.common import NotFoundError
from app.schemas.user import UserModel


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_by_id(self, _id: UUID) -> UserModel:
        user = await self.repo.get_by_id(_id)
        if not user:
            raise NotFoundError("User")
        return UserModel.model_validate(user)


    async def get_user_by_email(self, email: str) -> UserModel:
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFoundError("User")
        return UserModel.model_validate(user)
