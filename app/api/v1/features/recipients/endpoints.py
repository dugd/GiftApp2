from uuid import UUID
from fastapi import APIRouter, status, Depends

from app.service.recipient import RecipientService
from app.schemas.recipient import RecipientCreate, RecipientModel, RecipientUpdateInfo, \
    RecipientUpdateBirthday
from app.api.v1.dependencies import CurrentUserDepends, CurrentSimpleUser
from .dependencies import get_recipient_service


router = APIRouter(prefix="/recipients", tags=["recipients"])


@router.get("/", response_model=list[RecipientModel])
async def index(
        user: CurrentUserDepends,
        recipient_service: RecipientService = Depends(get_recipient_service),
):
    """Get list of recipients"""
    recipients = await recipient_service.list(user)

    return recipients


@router.get("/{recipient_id}", response_model=RecipientModel)
async def get(
        user: CurrentUserDepends,
        recipient_id: UUID,
        recipient_service: RecipientService = Depends(get_recipient_service),
):
    """Get recipient by ID"""
    recipient = await recipient_service.get_recipient(recipient_id, user)
    return recipient


@router.post(
    "/", response_model=RecipientModel, status_code=status.HTTP_201_CREATED,
)
async def create(
        user: CurrentSimpleUser,
        data: RecipientCreate,
        recipient_service: RecipientService = Depends(get_recipient_service),
):
    """Create new recipient"""
    recipient = await recipient_service.create(user, data)

    return recipient


@router.patch("/{recipient_id}", response_model=RecipientModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        user: CurrentUserDepends,
        recipient_id: UUID,
        data: RecipientUpdateInfo,
        recipient_service: RecipientService = Depends(get_recipient_service),
):
    """Update recipient info"""
    updated = await recipient_service.update_info(recipient_id, user, data)

    return updated


@router.post("/{recipient_id}/set-birthday", response_model=RecipientModel, status_code=status.HTTP_202_ACCEPTED)
async def set_birthday(
        user: CurrentUserDepends,
        recipient_id: UUID,
        data: RecipientUpdateBirthday,
        recipient_service: RecipientService = Depends(get_recipient_service),
):
    """Set birthday for recipient"""
    updated = await recipient_service.update_birthday(recipient_id, user, data)

    return updated


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        user: CurrentUserDepends,
        recipient_id: UUID,
        recipient_service: RecipientService = Depends(get_recipient_service),
):
    """Delete recipient"""
    await recipient_service.delete(recipient_id, user)
