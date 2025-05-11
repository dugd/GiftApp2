from app.repositories.orm.user import UserRepository
from app.models import SimpleUser
from app.schemas.user import UserModel
from app.utils.security import (
    hash_password, verify_password, create_access_token, create_refresh_token
)
from app.exceptions.auth import EmailAlreadyTaken, WrongCredentials
from app.schemas.auth import UserRegister, TokenPair


async def register_user(user_data: UserRegister, repo: UserRepository) -> UserModel:
    existing_user = await repo.get_by_email(str(user_data.email))
    if existing_user:
        raise EmailAlreadyTaken(str(user_data.email))
    user = SimpleUser(
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )
    await repo.add(user)

    return UserModel.model_validate(user)


async def authenticate_user(email: str, password: str, repo: UserRepository) -> UserModel:
    user = await repo.get_by_email(str(email))
    if not user or not verify_password(password, user.hashed_password):
        raise WrongCredentials()
    return UserModel.model_validate(user)


def create_token_pair(user: UserModel) -> TokenPair:
    new_access_token = create_access_token(
        payload={"id": user.id.hex, "sub": user.email, "role": user.role.value, "type": "access"})
    new_refresh_token = create_refresh_token(payload={"id": user.id.hex, "type": "refresh"})

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)
