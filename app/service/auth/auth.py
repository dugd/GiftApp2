from uuid import UUID

from app.core.enums import TokenType
from app.repositories.orm.user import UserRepository
from app.schemas.user import UserModel
from app.utils.security import (
    verify_password, create_token
)
from app.exceptions.common import NotFoundError
from app.exceptions.auth import WrongCredentials, UserAlreadyActivated, UserIsNotActivated
from app.schemas.auth import TokenPair


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def activate_user(self, user_id: UUID) -> UserModel:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        if user.is_active:
            raise UserAlreadyActivated(user.username)

        user.is_active = True
        user = await self.repo.update(user, {})
        return UserModel.model_validate(user)

    async def authenticate_user(self, email: str, password: str) -> UserModel:
        user = await self.repo.get_by_email(str(email))
        if not user:
            raise WrongCredentials()
        if not user.is_active:
            raise UserIsNotActivated(user.username)
        if not verify_password(password, user.hashed_password):
            raise WrongCredentials()
        return UserModel.model_validate(user)

    @staticmethod
    def create_token_pair(user: UserModel) -> TokenPair:
        access_token = create_token(
            payload={
                "id": user.id.hex,
                "sub": user.email,
                "role": user.role.value,
                "type": TokenType.access.value
            },
            token_type=TokenType.access,
        )
        refresh_token = create_token(
            payload={"id": user.id.hex, "type": TokenType.refresh.value},
            token_type=TokenType.refresh,
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
