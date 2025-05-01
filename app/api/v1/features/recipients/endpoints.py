from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.features.recipients.models import Recipient
from app.api.v1.features.recipients.schemas import RecipientCreate, RecipientRead, RecipientUpdateInfo, \
    RecipientUpdateBirthday
from app.core.database import get_session
from app.api.v1.features.auth.models import User, UserRole
from app.api.v1.features.auth.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/recipients", tags=["recipients"])


async def get_recipient_or_404(db: AsyncSession, recipient_id: int, user: User) -> Recipient:
    stmt = select(Recipient).where(Recipient.id == recipient_id)
    if user.role == UserRole.USER.value:
        stmt = stmt.where(Recipient.user_id == user.id)
    result = await db.execute(stmt)
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    return recipient


@router.get("/", response_model=list[RecipientRead])
async def index(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Get list of recipients"""
    stmt = select(Recipient)
    if user.role == UserRole.USER.value:
        stmt = stmt.where(Recipient.user_id == user.id)
    result = await db.execute(stmt)
    recipients = result.scalars().all()
    return list(map(RecipientRead.model_validate, recipients))


@router.get("/{recipient_id}", response_model=RecipientRead)
async def get(
        recipient_id: int,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Get recipient by ID"""
    recipient = await get_recipient_or_404(db, recipient_id, user)
    return RecipientRead.model_validate(recipient)


@router.post(
    "/", response_model=RecipientRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(UserRole.USER.value))]
)
async def create(
        data: RecipientCreate,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Create new recipient"""
    recipient = Recipient(**data.model_dump(), user_id=user.id)
    db.add(recipient)
    await db.commit()

    return RecipientRead.model_validate(recipient)


@router.patch("/{recipient_id}", response_model=RecipientRead, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        recipient_id: int,
        data: RecipientUpdateInfo,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Update recipient info"""
    recipient = await get_recipient_or_404(db, recipient_id, user)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(recipient, key, value)

    await db.commit()

    return RecipientRead.model_validate(recipient)


@router.post("/{recipient_id}/set-birthday", response_model=RecipientRead, status_code=status.HTTP_202_ACCEPTED)
async def set_birthday(
        recipient_id: int,
        data: RecipientUpdateBirthday,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Set birthday for recipient"""
    recipient = await get_recipient_or_404(db, recipient_id, user)

    recipient.birthday = data.birthday

    await db.commit()

    return RecipientRead.model_validate(recipient)


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        recipient_id: int,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Delete recipient"""
    recipient = await get_recipient_or_404(db, recipient_id, user)

    await db.delete(recipient)

    await db.commit()
