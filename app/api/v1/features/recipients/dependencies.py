from typing import Optional

from pydantic import BaseModel
from fastapi import Query

from app.service.recipient import RecipientService, RecipientPolicy
from app.repositories.orm.recipient import RecipientRepository
from app.api.v1.dependencies import DBSessionDepends
from app.api.v1.pagination import BaseSortingParams


async def get_recipient_service(db: DBSessionDepends) -> RecipientService:
    return RecipientService(RecipientRepository(db), RecipientPolicy)


class RecipientFilterParams(BaseModel):
    name: Optional[str] = Query(default=None)
    relation: Optional[str] = Query(default=None)
    notes: Optional[str] = Query(default=None)

    def to_filters(self) -> dict:
        filters = {}
        if self.name:
            filters["name__icontains"] = self.name
        if self.relation:
            filters["relation__icontains"] = self.relation
        if self.notes:
            filters["notes__icontains"] = self.notes
        return filters


class RecipientSortingParams(BaseSortingParams):
    allowed_fields = {"name", "birthday", "relation"}