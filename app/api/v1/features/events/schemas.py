from typing import Optional, List
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
    is_repeating: bool
    type: EventType
    start_date: date
    created_at: datetime

    recipient_id: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventModel(EventBase):
    id: int

    creator_id: Optional[int] = None


class EventFull(EventModel):
    next_date: date = Field(alias="occurrence_date")


class EventUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None


class EventOccurrenceBase(BaseModel):
    occurrence_date: date
    created_at: datetime

    event_id: int


class EventOccurrenceModel(EventOccurrenceBase):
    id: int


class EventOccurrences(BaseModel):
    id: int
    occurrences: Optional[List[EventOccurrenceModel]] = None