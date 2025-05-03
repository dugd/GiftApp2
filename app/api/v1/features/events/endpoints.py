from datetime import date

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.sql import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.exceptions import NotFoundError
from app.api.v1.features.auth.dependencies import get_current_user
from app.api.v1.features.auth.models import User, SimpleUser, AdminUser
from app.api.v1.features.events.exceptions import PastEventError
from app.api.v1.features.events.schemas import (
    EventCreate, EventModel, EventFull, OccurrencesView, EventOccurrenceId, EventUpdate,
    EventNext, CalendarView, EventOccurrenceModel
)
from app.api.v1.features.events.service import event_create, event_update_info, event_delete, get_event
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
    try:
        event = await get_event(event_id, user, db)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    return event


@router.get("/", response_model=list[EventFull])
async def index(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get all (global and user`s) next planned events"""
    stmt = (select(Event, EventOccurrence)
            .join(EventOccurrence, Event.id == EventOccurrence.event_id).where(Event.deleted_at == None))
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))

    result = await db.execute(stmt)

    response = {}
    for event, occurrence in result.all():
        if event.id not in response:
            response[event.id] = EventFull.model_validate(event)
        response[event.id].occurrences.append(EventOccurrenceId.model_validate(occurrence))

    return response.values()


@router.get("/occurrences", response_model=OccurrencesView)
async def index_occurrences(
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """
    Fetches and processes occurrences of events within a specified date range. This function queries the database for
    events and their occurrences, processes them according to user type, and returns the data in a structured response
    format suitable for the expected response model.
    """
    stmt = (select(Event, EventOccurrence)
            .join(EventOccurrence, Event.id == EventOccurrence.event_id)
            .where(Event.deleted_at == None)
            .where(EventOccurrence.occurrence_date.between(from_date, to_date)))
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))

    result = await db.execute(stmt)

    response = OccurrencesView()
    for event, occurrence in result.all():
        if event.id not in response: response.root[event.id] = []

        response.root[event.id].append(EventOccurrenceId.model_validate(occurrence))

    return response


@router.get("/calendar", response_model=CalendarView)
async def calendar_view(
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Return calendar-style view: occurrences grouped by date."""
    stmt = (
        select(Event, EventOccurrence)
        .join(EventOccurrence, Event.id == EventOccurrence.event_id)
        .where(Event.deleted_at == None)
        .where(EventOccurrence.occurrence_date.between(from_date, to_date))
    )

    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))

    result = await db.execute(stmt)

    response = CalendarView()
    for event, occurrence in result.all():
        date_key = occurrence.occurrence_date
        if date_key not in response.root:
            response.root[date_key] = []
        response.root[date_key].append(EventOccurrenceModel.model_validate(occurrence))

    return response


@router.post("/", response_model=EventModel, status_code=status.HTTP_201_CREATED)
async def create(
        event_data: EventCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Create new event"""
    if isinstance(user, SimpleUser):
        if event_data.is_global:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden to create global event")
    if isinstance(user, AdminUser):
        if not event_data.is_global:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="admin event must be global")
        if event_data.recipient_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="admin event must not have recipient")

    try:
        response = await event_create(event_data, user.id, db)
    except PastEventError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event cannot be created in the past")

    return response


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
    event_occurrences = result.scalars().all()

    event_full = EventFull.model_validate(event)
    for occurrence in event_occurrences:
        event_full.occurrences.append(EventOccurrenceId.model_validate(occurrence))


    return event_full


@router.get("/{event_id}/info", response_model=EventModel)
async def get_info(
        event_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event info"""
    event = await get_event_or_404(event_id, user, db, find_global=True)

    return EventModel.model_validate(event)

@router.get("/{event_id}/next", response_model=EventNext)
async def get_next(
        event_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event with next occurrence"""
    event = await get_event_or_404(event_id, user, db, find_global=True)

    stmt = (select(EventOccurrence)
            .where(EventOccurrence.event_id == event.id)
            .where(EventOccurrence.occurrence_date >= date.today())
            .order_by(EventOccurrence.occurrence_date.asc())
            .limit(1))
    result = await db.execute(stmt)
    occurrence = result.scalar_one_or_none()

    response = EventNext.model_validate(event)
    if occurrence:
        response.occurrence = EventOccurrenceId.model_validate(occurrence)
    return response

@router.patch("/{event_id}", response_model=EventModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        event_id: int,
        data: EventUpdate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """update title, type fields"""
    event = await get_event_or_404(event_id, user, db, find_global=False)
    updated = await event_update_info(event, data, db)

    return EventModel.model_validate(updated)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        event_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """delete event (set to inactive)"""
    event = await get_event_or_404(event_id, user, db, True)
    if isinstance(user, SimpleUser):
        if event.is_global:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden to delete global event")

    await event_delete(event, db)


@router.get(
    "/{event_id}/occurrences", response_model=list[EventOccurrenceId])
async def get_occurrences(
        event_id: int,
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event occurrences in date interval"""
    event = await get_event_or_404(event_id, user, db, find_global=True)

    stmt = (select(EventOccurrence)
            .where(EventOccurrence.event_id == event.id)
            .where(EventOccurrence.occurrence_date.between(from_date, to_date)))
    result = await db.execute(stmt)
    event_occurrences = result.scalars().all()

    return list(map(EventOccurrenceId.model_validate, event_occurrences))
