from typing import Optional
from datetime import datetime, date
from enum import Enum

from pydantic import BaseModel, Field


class EventType(Enum):
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    HOLIDAY = "HOLIDAY"
    OTHER = "OTHER"


class EventBase(BaseModel):
    title: str
    is_global: bool
    type: EventType
    rule: str
    start_date: date
    created_at: datetime

    user_id: Optional[int] = None
    recipient_id: Optional[int] = None


class EventFirstBase(BaseModel):
    title: str
    is_global: bool
    type: EventType
    rule: str
    start_date: date
    next_date: date = Field(alias="occurrence_date")
    created_at: datetime

    user_id: Optional[int] = None
    recipient_id: Optional[int] = None


class EventOccurrenceBase(BaseModel):
    occurrence_date: date
    created_at: datetime

    event_id: int