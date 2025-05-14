from app.mail import MailSender
from app.repositories.orm import UserRepository
from app.service.auth import UserRegistrationService, AuthService
from app.service.user import UserService
from app.api.v1.dependencies import DBSessionDepends


async def get_register_service(db: DBSessionDepends):
    return UserRegistrationService(UserRepository(db), MailSender())


async def get_auth_service(db: DBSessionDepends):
    return AuthService(UserRepository(db))


async def get_user_service(db: DBSessionDepends):
    return UserService(UserRepository(db))
