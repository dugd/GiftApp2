from uuid import UUID

from app.repositories.orm.user import UserRepository
from app.exceptions.common import NotFoundError
from app.schemas.user import UserModel, UserUpdate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_by_id(self, _id: UUID) -> UserModel:
        user = await self.repo.get_by_id(_id)
        if not user:
            raise NotFoundError("User")
        return UserModel.model_validate(user)

    async def update_profile(self, user_id: UUID, data: UserUpdate) -> UserModel:
        user = await self.repo.get_by_id(user_id)
        updated = await self.repo.update(user, data.model_dump(exclude_unset=True))
        return UserModel.model_validate(updated)

    async def attach_avatar(self, user_id: UUID, media_id: UUID) -> UserModel:
        user = await self.repo.get_by_id(user_id)
        user.ava_id = media_id
        updated = await self.repo.update(user, {})
        return UserModel.model_validate(updated)
