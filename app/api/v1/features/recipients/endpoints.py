from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Recipient, User, UserRole
from app.api.v1.features.exceptions import NotFoundError
from app.api.v1.features.auth.dependencies import get_current_user, RoleChecker
from app.api.v1.features.recipients.schemas import RecipientCreate, RecipientRead, RecipientUpdateInfo, \
    RecipientUpdateBirthday
from app.api.v1.features.recipients.service import get_recipient, recipient_create, recipient_update_info, \
    recipient_delete, get_recipient_list

router = APIRouter(prefix="/recipients", tags=["recipients"])


async def get_recipient_or_404(db: AsyncSession, recipient_id: int, user: User) -> Recipient:
    try:
        return await get_recipient(recipient_id, user, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")


@router.get("/", response_model=list[RecipientRead])
async def index(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
):
    """Get list of recipients"""
    recipients = await get_recipient_list(user, db)
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
    recipient = await recipient_create(data, user.id, db)

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

    updated = recipient_update_info(recipient, data, db)

    return RecipientRead.model_validate(updated)


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

    await recipient_delete(recipient, db)
