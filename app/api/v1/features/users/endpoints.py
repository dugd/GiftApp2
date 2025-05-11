from fastapi import APIRouter

from app.schemas.user import UserRead
from app.api.v1.dependencies import CurrentUserDepends


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUserDepends):
    return UserRead(**current_user.model_dump())
