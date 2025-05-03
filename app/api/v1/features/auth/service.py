from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.auth.security import hash_password, verify_password
from app.api.v1.features.auth.models import User, SimpleUser
from app.api.v1.features.auth.security import create_access_token, create_refresh_token
from app.api.v1.features.auth.schemas import UserRegister, TokenPair
from app.api.v1.features.auth.exceptions import EmailAlreadyTaken, WrongCredentials

async def register_user(user_data: UserRegister, db: AsyncSession) -> User:
    existing_user = await get_user_by_email(str(user_data.email), db)
    if existing_user:
        raise EmailAlreadyTaken("Email already registered")
    user = SimpleUser(
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    await db.commit()

    return user


async def authenticate_user(email: str, password: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    if not user or verify_password(password, user.hashed_password):
        raise WrongCredentials("Incorrect credentials")


def create_token_pair(user: User) -> TokenPair:
    new_access_token = create_access_token(
        payload={"id": user.id, "sub": user.email, "role": user.role, "type": "access"})
    new_refresh_token = create_refresh_token(payload={"id": user.id, "type": "refresh"})

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)


async def get_user_by_id(_id: int, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.id == _id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()