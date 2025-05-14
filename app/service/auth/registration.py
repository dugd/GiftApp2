from typing import Protocol

from app.core.enums import TokenType
from app.mail import MailSender, generate_activate_account_email
from app.repositories.orm.user import UserRepository
from app.models import SimpleUser, AdminUser
from app.schemas.user import UserModel
from app.utils.security import (
    hash_password, create_token
)
from app.exceptions.auth import EmailAlreadyTaken
from app.schemas.auth import UserRegister


class RegistrationService(Protocol):
    async def register(self, user_data: UserRegister) -> UserModel:
        ...


class UserRegistrationService:
    def __init__(self, repo: UserRepository, mail_sender: MailSender):
        self.repo = repo
        self.mail_sender = mail_sender

    async def register(self, user_data: UserRegister) -> UserModel:
        existing_user = await self.repo.get_by_email(str(user_data.email))
        if existing_user:
            raise EmailAlreadyTaken(str(user_data.email))

        user = SimpleUser(
            email=str(user_data.email),
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            is_active=False,
        )
        await self.repo.add(user)
        user_model = UserModel.model_validate(user)

        activation_token = create_token(
            {"id": user_model.id.hex, "type": TokenType.activation.value},
            TokenType.activation
        )

        email_data = await generate_activate_account_email(
            email_to=str(user_model.email),
            token=activation_token,
        )

        self.mail_sender.send_mail(
            to=str(user_model.email),
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

        return user_model


class AdminRegistrationService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(self, user_data: UserRegister) -> UserModel:
        existing_user = await self.repo.get_by_email(str(user_data.email))
        if existing_user:
            raise EmailAlreadyTaken(str(user_data.email))

        user = AdminUser(
            email=str(user_data.email),
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            is_active=True,
        )
        await self.repo.add(user)
        user_model = UserModel.model_validate(user)

        return user_model