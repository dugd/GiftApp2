from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user_by_id(_id: int, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.id == _id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
