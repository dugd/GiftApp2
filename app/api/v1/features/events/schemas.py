from typing import Optional, List, Dict
from datetime import datetime, date

from pydantic import BaseModel, RootModel, ConfigDict

from app.models.events import EventType


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
    occurrences: List[EventOccurrenceId] = []


class EventNext(EventModel):
    occurrence: Optional[EventOccurrenceId] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[EventType] = None


class OccurrencesView(RootModel):
    root: Dict[int, List[EventOccurrenceId]] = {}

class CalendarView(RootModel):
    root: Dict[date, List[EventOccurrenceModel]] = {}