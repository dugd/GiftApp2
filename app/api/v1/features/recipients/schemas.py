from typing import List, Optional
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecipientBase(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    birthday: date
    relation: str = Field(min_length=2, max_length=32)
    preferences: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = None

    @classmethod
    @field_validator("birthday")
    def validate_birthday(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Birthday must be in the past")
        if v < date(1900, 1, 1):
            raise ValueError("Birthday is too far in the past (more than 1900)")
        return v


class RecipientCreate(RecipientBase):
    pass


class RecipientRead(RecipientBase):
    id: int

    model_config =ConfigDict(from_attributes=True)


class RecipientUpdateInfo(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=32)
    relation: Optional[str] = Field(default=None, min_length=2, max_length=32)
    preferences: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = None


class RecipientUpdateBirthday(BaseModel):
    birthday: date

    @classmethod
    @field_validator("birthday")
    def validate_birthday(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Birthday must be in the past")
        if v < date(1900, 1, 1):
            raise ValueError("Birthday is too far in the past (more than 1900)")
        return v