from typing import Optional

from pydantic import BaseModel
from fastapi import Query

from app.service.idea import IdeaService, IdeaPolicy
from app.repositories.orm import IdeaRepository
from app.api.v1.dependencies import DBSessionDepends
from app.api.v1.pagination import BaseSortingParams


async def get_idea_service(db: DBSessionDepends) -> IdeaService:
    return IdeaService(IdeaRepository(db), IdeaPolicy)


class IdeaFilterParams(BaseModel):
    title: Optional[str] = Query(default=None)
    description: Optional[str] = Query(default=None)
    archived: bool = Query(default=False)

    def to_filters(self) -> dict:
        filters = {}
        if self.title:
            filters["title__icontains"] = self.title
        if self.description:
            filters["description__icontains"] = self.description
        filters["is_archived"] = self.archived
        return filters


class IdeaSortingParams(BaseSortingParams):
    allowed_fields = {"title", "created_at", "updated_at", "estimated_price"}