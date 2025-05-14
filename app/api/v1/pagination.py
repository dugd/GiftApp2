from fastapi import Query
from pydantic import BaseModel, field_validator
from typing import Optional


class PaginationParams(BaseModel):
    limit: int = Query(default=20, ge=1, le=100)
    offset: int = Query(default=0, ge=0)
    order_by: Optional[str] = Query(default=None, description="Field to sort by")
    desc: bool = Query(default=False, description="Sort descending")

    @classmethod
    @field_validator("order_by")
    def strip_order_by(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v