from typing import List, Optional
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecipientBase(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    birthday: date
    relation: str = Field(min_length=2, max_length=32)
    preferences: Optional[List[str]] = Field(default=None, min_length=1, max_length=10)
    notes: Optional[str] = None

    @field_validator("birthday")
    def validate_birthday(self, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Birthday must be in the past")
        max_past = date(1900, 1, 1)
        if v < max_past:
            raise ValueError(f"Birthday is too far in the past (more than {max_past.year})")
        return v


class RecipientCreate(RecipientBase):
    pass


class RecipientRead(RecipientBase):
    id: int

    model_config =ConfigDict(from_attributes=True)


class RecipientUpdateInfo(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=32)
    relation: Optional[str] = Field(default=None, min_length=2, max_length=32)
    preferences: Optional[List[str]] = Field(default=None, min_length=1, max_length=10)
    notes: Optional[str] = None


class RecipientUpdateBirthday(BaseModel):
    birthday: date

    @field_validator("birthday")
    def validate_birthday(self, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Birthday must be in the past")
        max_past = date(1900, 1, 1)
        if v < max_past:
            raise ValueError(f"Birthday is too far in the past (more than {max_past.year})")
        return v