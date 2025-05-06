from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Recipient, UserRole
from app.exceptions.exceptions import NotFoundError
from app.schemas.recipient import RecipientCreate, RecipientUpdateInfo, RecipientUpdateBirthday, RecipientModel
from app.schemas.user import UserModel


async def _get_recipient_by_id(recipient_id: UUID, db: AsyncSession) -> Recipient:
    stmt = select(Recipient).where(Recipient.id == recipient_id)
    result = await db.execute(stmt)
    recipient = result.scalar_one_or_none()
    return recipient


async def _get_recipient_list(db: AsyncSession) -> Sequence[Recipient]:
    stmt = select(Recipient)
    result = await db.execute(stmt)
    recipients = result.scalars().all()
    return recipients


async def _get_user_recipient_list(user_id: UUID, db: AsyncSession) -> Sequence[Recipient]:
    stmt = select(Recipient).where(Recipient.user_id == user_id)
    result = await db.execute(stmt)
    recipients = result.scalars().all()
    return recipients


async def recipient_create(data: RecipientCreate, user_id: UUID, db: AsyncSession) -> RecipientModel:
    recipient = Recipient(**data.model_dump(), user_id=user_id)
    db.add(recipient)
    await db.commit()
    return RecipientModel.model_validate(recipient)


async def recipient_update_info(recipient_id: UUID, data: RecipientUpdateInfo, db: AsyncSession) -> RecipientModel:
    recipient = await _get_recipient_by_id(recipient_id, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(recipient, key, value)
    await db.commit()
    return RecipientModel.model_validate(recipient)


async def recipient_update_birthday(recipient_id: UUID, data: RecipientUpdateBirthday, db: AsyncSession) -> RecipientModel:
    recipient = await _get_recipient_by_id(recipient_id, db)
    recipient.birthday = data.birthday
    await db.commit()
    return RecipientModel.model_validate(recipient)


async def recipient_delete(recipient_id: UUID, db: AsyncSession):
    recipient = await _get_recipient_by_id(recipient_id, db)
    await db.delete(recipient)
    await db.commit()


async def get_recipient(recipient_id: UUID, db: AsyncSession) -> RecipientModel:
    recipient = await _get_recipient_by_id(recipient_id, db)
    if not recipient:
        raise NotFoundError("Recipient")
    return RecipientModel.model_validate(recipient)


async def get_recipient_list(user: UserModel, db: AsyncSession) -> Sequence[RecipientModel]:
    if user.role == UserRole.USER.value:
        recipients = await _get_user_recipient_list(user.id, db)
    else:
        recipients = await _get_recipient_list(db)
    return [RecipientModel.model_validate(recipient) for recipient in recipients]
