from datetime import date

from fastapi import APIRouter, status

from app.api.v1.features.events.schemas import (
    EventCreate, EventModel, EventFull, EventOccurrenceModel, EventOccurrences
)


router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[EventFull])
async def index():
    """Get all (global and user`s) next planned events"""
    pass


@router.get("/occurrences", response_model=list[EventOccurrences])
async def index_occurrences(from_date: date, to_date: date):
    """Get all event occurrences in date interval"""
    pass


@router.post("/", response_model=EventModel, status_code=status.HTTP_201_CREATED)
async def create(event_data: EventCreate):
    """Create new event"""
    pass


@router.get("/{event_id}", response_model=EventFull)
async def get():
    """Create next planned event"""
    pass


@router.patch("/{event_id}", response_model=EventModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info():
    """update title, type fields"""
    pass


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete():
    """delete event (set to inactive)"""
    pass


@router.get(
    "/{event_id}/occurrences", response_model=list[EventOccurrenceModel])
async def get_occurrences(from_date: date, to_date: date):
    """Get event occurrences in date interval"""
    pass
