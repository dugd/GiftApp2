from uuid import UUID

from app.mail import MailSender, generate_activate_account_email
from app.repositories.orm.user import UserRepository
from app.models import SimpleUser
from app.schemas.user import UserModel
from app.utils.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, create_activation_token, decode_token
)
from app.exceptions.common import NotFoundError
from app.exceptions.auth import EmailAlreadyTaken, WrongCredentials, UserAlreadyActivated
from app.schemas.auth import UserRegister, TokenPair


async def register_user(user_data: UserRegister, repo: UserRepository, mail_sender: MailSender) -> UserModel:
    existing_user = await repo.get_by_email(str(user_data.email))
    if existing_user:
        raise EmailAlreadyTaken(str(user_data.email))


    user = SimpleUser(
        email=str(user_data.email),
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        is_active=False,
    )
    await repo.add(user)
    user_model = UserModel.model_validate(user)

    activation_token = create_activation_token({"id": user_model.id.hex, "type": "activation"})
    email_data = await generate_activate_account_email(
        email_to=str(user_model.email),
        token=activation_token,
    )

    mail_sender.send_mail(
        to=str(user_model.email),
        subject=email_data.subject,
        html_content=email_data.html_content,
    )

    return user_model


async def activate_user(user_id: UUID, repo: UserRepository) -> UserModel:

    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError("User")

    if user.is_active:
        raise UserAlreadyActivated(user.username)

    user.is_active = True
    user = await repo.update(user, {})
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
