from datetime import date, datetime

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.auth.dependencies import get_current_user
from app.api.v1.features.auth.models import User, SimpleUser, AdminUser, RootUser, UserRole
from app.api.v1.features.events.schemas import (
    EventCreate, EventModel, EventFull, EventOccurrenceModel, EventOccurrences, EventOccurrenceId, EventUpdate
)
from app.api.v1.features.events.models import Event, EventOccurrence
from app.core.database import get_session

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
async def create(
        event_data: EventCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session)):
    """Create new event"""
    if isinstance(user, AdminUser):
        if event_data.is_global:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden to create global event")
    if isinstance(user, AdminUser):
        if not event_data.is_global:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="admin event must be global")
        if event_data.recipient_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="admin event must not have recipient")

    event = Event(**event_data.model_dump(), user_id=user.id)
    db.add(event)
    await db.flush()

    event_occurrence = EventOccurrence(
        occurrence_date=event_data.start_date,
        event_id=event.id,
        created_at=datetime.now()
    )
    db.add(event_occurrence)

    await db.commit()

    return EventModel.model_validate(Event)




@router.get("/{event_id}", response_model=EventFull)
async def get(
        event_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Create next planned event"""
    stmt = select(Event).where(Event.id == event_id)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    stmt = select(EventOccurrence).where(EventOccurrence.id == event.id)
    result = await db.execute(stmt)
    event_occurrence = result.scalar_one_or_none()

    event_full = EventFull(**EventModel.model_validate(event).model_dump())
    event_full.next_occurrence = EventOccurrenceId.model_validate(event_occurrence)
    return event_full


@router.patch("/{event_id}", response_model=EventModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        event_id: int,
        data: EventUpdate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """update title, type fields"""
    stmt = select(Event).where(Event.id == event_id)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    await db.commit()

    return EventModel.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        event_id: int,
):
    """delete event (set to inactive)"""
    pass


@router.get(
    "/{event_id}/occurrences", response_model=list[EventOccurrenceModel])
async def get_occurrences(from_date: date, to_date: date):
    """Get event occurrences in date interval"""
    pass
