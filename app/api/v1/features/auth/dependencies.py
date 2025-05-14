from app.mail import MailSender
from app.repositories.orm import UserRepository
from app.service.auth import RegistrationService, UserRegistrationService, AdminRegistrationService, AuthService
from app.api.v1.dependencies import DBSessionDepends


async def get_user_register_service(db: DBSessionDepends) -> RegistrationService:
    return UserRegistrationService(UserRepository(db), MailSender())


async def get_admin_register_service(db: DBSessionDepends) -> RegistrationService:
    return AdminRegistrationService(UserRepository(db))


async def get_auth_service(db: DBSessionDepends):
    return AuthService(UserRepository(db))
