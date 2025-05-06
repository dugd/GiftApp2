from uuid import UUID
from datetime import date
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import User, SimpleUser, AdminUser, UserRole, Event
from app.exceptions.event.exceptions import PastEventError
from app.service.event_service import event_create, event_update_info, event_delete, get_event, get_event_list, \
    get_next_occurrence, generate_missing_occurrences
from app.schemas.event_schemas import (
    EventCreate, EventModel, EventFull, OccurrencesView, EventOccurrenceId, EventUpdate,
    EventNext, CalendarView, EventOccurrenceModel
)
from app.api.v1.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/events", tags=["events"])


async def get_event_or_404(
        event_id: UUID,
        user: User,
        db: AsyncSession,
        with_occurrence: bool = False,
) -> Event:
    """Fetch an event by ID with user-specific access control, or raise 404."""
    event = await get_event(event_id, user, db, with_occurrence=with_occurrence)

    return event


@router.get("/", response_model=list[EventFull])
async def index(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get all (global and user`s) next planned events"""
    events = await get_event_list(user, db, with_occurrence=True)
    response = []
    for event in events:
        model = EventFull.model_validate(event)
        response.append(model)

    return response


@router.get("/occurrences", response_model=OccurrencesView)
async def index_occurrences(
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """
    Fetches and processes occurrences of events within a specified date range. This function queries the models for
    events and their occurrences, processes them according to user type, and returns the data in a structured response
    format suitable for the expected response model.
    """
    events = await get_event_list(user, db, with_occurrence=True)

    response = OccurrencesView()
    for event in events:
        response.root[event.id] = [EventOccurrenceId.model_validate(occur) for occur in event.occurrences]

    return response


@router.post(
    "/occurrences/generate",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(UserRole.ROOT.value))])
async def manual_generate(
        db: AsyncSession = Depends(get_session),
):
        created = await generate_missing_occurrences(db)
        return {"created": created}


@router.get("/calendar", response_model=CalendarView)
async def calendar_view(
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Return calendar-style view: occurrences grouped by date."""
    events = await get_event_list(user, db, with_occurrence=True)

    response = CalendarView()
    for event in events:
        for occur in event.occurrences:
            date_key = occur.occurrence_date
            if date_key not in response.root:
                response.root[date_key] = []
            response.root[date_key].append(EventOccurrenceModel.model_validate(occur))

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
        event_id: UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event"""
    event = await get_event_or_404(event_id, user, db, with_occurrence=True)

    event_full = EventFull.model_validate(event)

    return event_full


@router.get("/{event_id}/info", response_model=EventModel)
async def get_info(
        event_id: UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event info"""
    event = await get_event_or_404(event_id, user, db, with_occurrence=False)

    return EventModel.model_validate(event)

@router.get("/{event_id}/next", response_model=EventNext)
async def get_next(
        event_id: UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event with next occurrence"""
    event = await get_event_or_404(event_id, user, db)
    occurrence = await get_next_occurrence(event_id, db)

    response = EventNext.model_validate(event)
    if occurrence:
        response.occurrence = EventOccurrenceId.model_validate(occurrence)
    return response

@router.patch("/{event_id}", response_model=EventModel, status_code=status.HTTP_202_ACCEPTED)
async def update_info(
        event_id: UUID,
        data: EventUpdate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """update title, type fields"""
    event = await get_event_or_404(event_id, user, db, with_occurrence=False)
    if isinstance(user, SimpleUser):
        if event.is_global:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden to change global event")
    updated = await event_update_info(event, data, db)

    return EventModel.model_validate(updated)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
        event_id: UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """delete event (set to inactive)"""
    event = await get_event_or_404(event_id, user, db, with_occurrence=False)
    if isinstance(user, SimpleUser):
        if event.is_global:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden to delete global event")

    await event_delete(event, db)


@router.get(
    "/{event_id}/occurrences", response_model=list[EventOccurrenceId])
async def get_occurrences(
        event_id: UUID,
        from_date: date,
        to_date: date,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session),
):
    """Get event occurrences in date interval"""
    event = await get_event_or_404(event_id, user, db, with_occurrence=True)

    response = [EventOccurrenceId.model_validate(occur) for occur in event.occurrences]

    return response
