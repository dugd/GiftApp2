from typing import Optional, ClassVar

from fastapi import Query
from pydantic import BaseModel, field_validator


class PaginationParams(BaseModel):
    limit: int = Query(default=20, ge=1, le=100)
    offset: int = Query(default=0, ge=0)


class BaseSortingParams(BaseModel):
    order_by: Optional[str] = Query(None)
    desc: bool = Query(False)

    allowed_fields: ClassVar[set[str]] = set()

    @field_validator("order_by")
    @classmethod
    def validate_order_by(cls, v: Optional[str]) -> Optional[str]:
        if v and cls.allowed_fields and v not in cls.allowed_fields:
            raise ValueError(f"Invalid field for sorting: '{v}'")
        return v