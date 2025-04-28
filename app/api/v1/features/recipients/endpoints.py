from fastapi import APIRouter, status

from app.api.v1.features.recipients.schemas import RecipientCreate, RecipientRead, RecipientUpdateInfo, RecipientUpdateBirthday

router = APIRouter(prefix="/recipients", tags=["recipients"])


@router.get("/", response_model=list[RecipientRead])
async def index():
    """get list of recipients"""
    pass


@router.get("/{recipient_id}", response_model=RecipientRead)
async def get(recipient_id: int):
    """get recipient by id"""
    pass


@router.post("/", response_model=RecipientRead, status_code=status.HTTP_201_CREATED)
async def create(data: RecipientCreate):
    """create new recipient"""
    pass


@router.patch("/{recipient_id}", response_model=RecipientRead, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        recipient_id: int,
        data: RecipientUpdateInfo,
):
    """update recipient info"""
    pass


@router.post("/{recipient_id}/set-birthday", response_model=RecipientRead, status_code=status.HTTP_202_ACCEPTED)
async def set_birthday(
        recipient_id: int,
        data: RecipientUpdateBirthday,
):
    """set birthday"""
    pass


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(recipient_id: int):
    """delete recipient"""
    pass