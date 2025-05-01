from datetime import date, datetime

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.sql import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.auth.dependencies import get_current_user
from app.api.v1.features.auth.models import User, SimpleUser, AdminUser
from app.api.v1.features.events.schemas import (
    EventCreate, EventModel, EventFull, EventOccurrenceModel, EventOccurrences, EventOccurrenceId, EventUpdate
)
from app.api.v1.features.events.models import Event, EventOccurrence
from app.core.database import get_session

router = APIRouter(prefix="/events", tags=["events"])


async def get_event_or_404(
        event_id: int,
        user: User,
        db: AsyncSession,
        find_global: bool = True,
) -> Event:
    """Fetch an event by ID with user-specific access control, or raise 404."""
    stmt = select(Event).where(Event.id == event_id)
    if isinstance(user, SimpleUser):
        stmt = stmt.where(
            or_(Event.user_id == user.id, Event.is_global)
            if find_global else
            (Event.user_id == user.id)
        )
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event



@router.get("/", response_model=list[EventFull])
async def index(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get all (global and user`s) next planned events"""
    stmt = select(Event, EventOccurrence).join(EventOccurrence, Event.id == EventOccurrence.event_id)
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))

    result = await db.execute(stmt)

    # does not work with several occurrences per event
    response = []
    for event, occurrence in result.all():
        event_full = EventFull(**EventModel.model_validate(event).model_dump())
        event_full.next_occurrence = EventOccurrenceId.model_validate(occurrence)
        response.append(event_full)

    return response


@router.get("/occurrences", response_model=list[EventOccurrences])
async def index_occurrences(
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get all event occurrences in date interval"""
    stmt = select(Event, EventOccurrence).join(EventOccurrence, Event.id == EventOccurrence.event_id)
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))

    result = await db.execute(stmt)

    response = {}
    for event, occurrence in result.all():
        if event.id not in response: response[event.id] = EventOccurrences(id=event.id)

        response[event.id].occurrences.append(EventOccurrenceId.model_validate(occurrence))

    return response.values()


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
    """Get event"""
    event = await get_event_or_404(event_id, user, db, find_global=False)

    stmt = select(EventOccurrence).where(EventOccurrence.event_id == event.id)
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
    event = get_event_or_404(event_id, user, db, find_global=False)

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
async def get_occurrences(
        event_id: int,
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event occurrences in date interval"""
    event = await get_event_or_404(event_id, user, db, find_global=True)

    stmt = select(EventOccurrence).where(EventOccurrence.event_id == event.id)
    result = await db.execute(stmt)
    event_occurrences = result.scalars().all()

    return list(map(EventOccurrenceModel.model_validate, event_occurrences))
