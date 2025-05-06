from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from app.schemas.idea_schemas import IdeaCreate, IdeaModel, IdeaUpdateInfo
from app.service.idea_service import IdeaService
from app.api.v1.dependencies import DBSessionDepends, CurrentUserDepends

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("/", response_model=IdeaModel, status_code=status.HTTP_201_CREATED)
async def create(
        user: CurrentUserDepends,
        db: DBSessionDepends,
        data: IdeaCreate,
):
    service = IdeaService(db)
    return await service.create_idea(data, user)


@router.get("/my", response_model=List[IdeaModel])
async def index_my(
        user: CurrentUserDepends,
        db: DBSessionDepends,
        archived: bool = False,
):
    service = IdeaService(db)
    return await service.get_users_ideas_list(user.id)


@router.get("/global", response_model=List[IdeaModel])
async def index_global(
        _: CurrentUserDepends,
        db: DBSessionDepends,
        archived: bool = False,
):
    service = IdeaService(db)
    return await service.get_global_ideas_list()


@router.get("/{idea_id}", response_model=List[IdeaModel])
async def get(
        user: CurrentUserDepends,
        db: DBSessionDepends,
        idea_id: UUID,
):
    service = IdeaService(db)
    return await service.get_idea_by_id(idea_id, user)


@router.patch("/{idea_id}", response_model=List[IdeaModel], status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        user: CurrentUserDepends,
        db: DBSessionDepends,
        idea_id: UUID,
        data: IdeaUpdateInfo,
):
    service = IdeaService(db)
    return await service.update_idea_info(idea_id, data, user)


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        user: CurrentUserDepends,
        db: DBSessionDepends,
        idea_id: UUID,
):
    service = IdeaService(db)
    await service.soft_delete_idea(idea_id, user)


router.post("/{idea_id}/archive", response_model=List[IdeaModel], status_code=status.HTTP_202_ACCEPTED)
async def archive(
        user: CurrentUserDepends,
        db: DBSessionDepends,
        idea_id: UUID,
):
    service = IdeaService(db)
    return await service.archive_idea(idea_id, user)