from typing import Optional, List
from datetime import datetime, date

from pydantic import BaseModel, ConfigDict

from app.api.v1.features.events.models import EventType


class EventBase(BaseModel):
    title: str
    is_global: bool
    is_repeating: bool
    type: EventType
    start_date: date

    recipient_id: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventModel(EventBase):
    id: int

    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class EventOccurrenceId(BaseModel):
    id: int
    occurrence_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventOccurrenceModel(EventOccurrenceId):
    event_id: int


class EventFull(EventModel):
    next_occurrence: Optional[EventOccurrenceId] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None


class EventOccurrences(BaseModel):
    id: int
    occurrences: List[EventOccurrenceId] = []