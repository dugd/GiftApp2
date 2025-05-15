from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends

from app.schemas.idea import IdeaCreate, IdeaModel, IdeaUpdateInfo
from app.service.idea import IdeaService
from app.api.v1.dependencies import CurrentUserDepends
from app.api.v1.pagination import PaginationParams
from .dependencies import get_idea_service, IdeaFilterParams, IdeaSortingParams

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("/", response_model=IdeaModel, status_code=status.HTTP_201_CREATED)
async def create(
        user: CurrentUserDepends,
        data: IdeaCreate,
        idea_service: IdeaService = Depends(get_idea_service),
):
    return await idea_service.create(user, data)


@router.get("/my", response_model=List[IdeaModel])
async def index_my(
        user: CurrentUserDepends,
        pagination: PaginationParams = Depends(),
        sorting: IdeaSortingParams = Depends(),
        filters: IdeaFilterParams = Depends(),
        idea_service: IdeaService = Depends(get_idea_service),
):
    return await idea_service.get_user_ideas(
        user,
        pagination.limit,
        pagination.offset,
        sorting.order_by,
        sorting.desc,
        filters.to_filters()
    )


@router.get("/global", response_model=List[IdeaModel])
async def index_global(
        user: CurrentUserDepends,
        pagination: PaginationParams = Depends(),
        sorting: IdeaSortingParams = Depends(),
        filters: IdeaFilterParams = Depends(),
        idea_service: IdeaService = Depends(get_idea_service),
):
    return await idea_service.get_global_ideas(
        pagination.limit,
        pagination.offset,
        sorting.order_by,
        sorting.desc,
        filters.to_filters()
    )


@router.get("/{idea_id}", response_model=IdeaModel)
async def get(
        user: CurrentUserDepends,
        idea_id: UUID,
        idea_service: IdeaService = Depends(get_idea_service),
):
    return await idea_service.get_one(user, idea_id)


@router.patch("/{idea_id}", response_model=IdeaModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        user: CurrentUserDepends,
        idea_id: UUID,
        data: IdeaUpdateInfo,
        idea_service: IdeaService = Depends(get_idea_service),
):
    return await idea_service.update_info(user, idea_id, data)


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        user: CurrentUserDepends,
        idea_id: UUID,
        idea_service: IdeaService = Depends(get_idea_service),
):
    await idea_service.soft_delete(user, idea_id)


router.post("/{idea_id}/archive", response_model=IdeaModel, status_code=status.HTTP_202_ACCEPTED)
async def archive(
        user: CurrentUserDepends,
        idea_id: UUID,
        idea_service: IdeaService = Depends(get_idea_service),
):
    return await idea_service.archive(user, idea_id)