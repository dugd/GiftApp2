from typing import Optional

from pydantic import BaseModel
from fastapi import Query

from app.service.idea import IdeaService, IdeaPolicy
from app.repositories.orm import IdeaRepository
from app.api.v1.dependencies import DBSessionDepends
from app.api.v1.pagination import BaseSortingParams


async def get_idea_service(db: DBSessionDepends) -> IdeaService:
    return IdeaService(IdeaRepository(db), IdeaPolicy)