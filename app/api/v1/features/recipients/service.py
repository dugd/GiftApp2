from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipient, User, UserRole
from app.api.v1.exceptions import NotFoundError
from app.api.v1.features.recipients.schemas import RecipientCreate, RecipientUpdateInfo, RecipientUpdateBirthday


async def recipient_create(data: RecipientCreate, user_id: UUID, db: AsyncSession) -> Recipient:
    recipient = Recipient(**data.model_dump(), user_id=user_id)
    db.add(recipient)
    await db.commit()
    return recipient


async def recipient_update_info(recipient: Recipient, data: RecipientUpdateInfo, db: AsyncSession) -> Recipient:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(recipient, key, value)
    await db.commit()
    return recipient


async def recipient_update_birthday(recipient: Recipient, data: RecipientUpdateBirthday, db: AsyncSession) -> Recipient:
    recipient.birthday = data.birthday
    await db.commit()
    return recipient


async def recipient_delete(recipient: Recipient, db: AsyncSession):
    await db.delete(recipient)

    await db.commit()


async def get_recipient(recipient_id: UUID, user: User, db: AsyncSession) -> Recipient:
    stmt = select(Recipient).where(Recipient.id == recipient_id)
    if user.role == UserRole.USER.value:
        stmt = stmt.where(Recipient.user_id == user.id)
    result = await db.execute(stmt)
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise NotFoundError("Recipient")
    return recipient


async def get_recipient_list(user: User, db: AsyncSession) -> Sequence[Recipient]:
    stmt = select(Recipient)
    if user.role == UserRole.USER.value:
        stmt = stmt.where(Recipient.user_id == user.id)
    result = await db.execute(stmt)
    return result.scalars().all()