from uuid import UUID
from fastapi import APIRouter, status, Depends

from app.core.enums import UserRole
import app.service.recipient as recipient_service
from app.repositories.orm.recipient import RecipientRepository
from app.schemas.recipient import RecipientCreate, RecipientModel, RecipientUpdateInfo, \
    RecipientUpdateBirthday
from app.api.v1.dependencies import DBSessionDepends, CurrentUserDepends, RoleChecker

router = APIRouter(prefix="/recipients", tags=["recipients"])


@router.get("/", response_model=list[RecipientModel])
async def index(
        db: DBSessionDepends,
        user: CurrentUserDepends,
):
    """Get list of recipients"""
    recipients = await recipient_service.get_recipient_list(user, RecipientRepository(db))

    return recipients


@router.get("/{recipient_id}", response_model=RecipientModel)
async def get(
        db: DBSessionDepends,
        user: CurrentUserDepends,
        recipient_id: UUID,
):
    """Get recipient by ID"""
    recipient = await recipient_service.get_recipient(recipient_id, user, RecipientRepository(db))
    return recipient


@router.post(
    "/", response_model=RecipientModel, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(UserRole.USER.value))]
)
async def create(
        db: DBSessionDepends,
        user: CurrentUserDepends,
        data: RecipientCreate,
):
    """Create new recipient"""
    recipient = await recipient_service.recipient_create(data, user, RecipientRepository(db))

    return recipient


@router.patch("/{recipient_id}", response_model=RecipientModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        db: DBSessionDepends,
        user: CurrentUserDepends,
        recipient_id: UUID,
        data: RecipientUpdateInfo,
):
    """Update recipient info"""
    updated = await recipient_service.recipient_update_info(recipient_id, user, data, RecipientRepository(db))

    return updated


@router.post("/{recipient_id}/set-birthday", response_model=RecipientModel, status_code=status.HTTP_202_ACCEPTED)
async def set_birthday(
        db: DBSessionDepends,
        user: CurrentUserDepends,
        recipient_id: UUID,
        data: RecipientUpdateBirthday,
):
    """Set birthday for recipient"""
    updated = await recipient_service.recipient_update_birthday(recipient_id, user, data, RecipientRepository(db))

    return updated


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        db: DBSessionDepends,
        user: CurrentUserDepends,
        recipient_id: UUID,
):
    """Delete recipient"""
    await recipient_service.recipient_delete(recipient_id, user, RecipientRepository(db))
