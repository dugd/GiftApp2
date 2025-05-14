from uuid import UUID

from fastapi import APIRouter, status, Body

from app.schemas.user import UserRead, UserUpdate
from app.repositories.orm import UserRepository
from app.service.user import UserService
from app.api.v1.dependencies import CurrentUserDepends, DBSessionDepends


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUserDepends):
    return UserRead(**current_user.model_dump())


@router.patch("/me", response_model=UserRead, status_code=status.HTTP_202_ACCEPTED)
async def update_profile(
        data: UserUpdate,
        db: DBSessionDepends,
        current_user: CurrentUserDepends,
):
    service = UserService(UserRepository(db))
    updated = await service.update_profile(current_user.id, data)
    return updated


@router.post("/me/avatar", response_model=UserRead)
async def attach_avatar_to_me(
        db: DBSessionDepends,
        current_user=CurrentUserDepends,
        avatar_id: UUID = Body(..., embed=True),
):
    service = UserService(UserRepository(db))
    updated = await service.attach_avatar(current_user.id, avatar_id)
    return updated