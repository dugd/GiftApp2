from datetime import datetime, timezone, date
from typing import Sequence

from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, EventOccurrence, User, SimpleUser
from app.api.v1.exceptions import NotFoundError
from app.api.v1.features.events.exceptions import PastEventError
from app.api.v1.features.events.schemas import EventCreate, EventModel, EventUpdate


async def event_create(data: EventCreate, user_id: int, db: AsyncSession) -> EventModel:
    now = datetime.now(timezone.utc)
    if data.start_date < now.date():
        raise PastEventError("event cannot be created in the past")

    event = Event(**data.model_dump(), user_id=user_id)
    db.add(event)
    await db.flush()

    event_occurrence = EventOccurrence(
        occurrence_date=data.start_date,
        event_id=event.id,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.add(event_occurrence)
    await db.commit()

    return EventModel.model_validate(event)


async def generate_missing_occurrences(db: AsyncSession) -> int:
    today = date.today()
    created = 0

    stmt = (select(Event)
            .where(Event.deleted_at == None)
            .options(joinedload(Event.last_occurrence))
            .where(Event.is_repeating == True))
    result = await db.execute(stmt)
    events = result.scalars().all()

    for event in events:
        last_occ = event.last_occurrence
        if not last_occ:
            last_occ = EventOccurrence(
                event_id=event.id,
                occurrence_date=event.start_date,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.add(last_occ)
            created += 1

        last_date = last_occ.occurrence_date

        while last_date < today:
            next_date = last_date + relativedelta(years=1)
            last_occ = EventOccurrence(
                event_id=event.id,
                occurrence_date=next_date,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.add(last_occ)
            last_date = next_date
            created += 1

    await db.commit()
    return created


async def event_update_info(event: Event, data: EventUpdate, db: AsyncSession) -> Event:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    await db.commit()

    return event


async def event_delete(event: Event, db: AsyncSession):
    event.soft_delete()
    await db.commit()


async def get_event(event_id: int, user: User, db: AsyncSession, with_occurrence: bool = False) -> Event:
    stmt = select(Event).where(Event.id == event_id).where(Event.deleted_at == None)
    if with_occurrence:
        stmt = stmt.options(selectinload(Event.occurrences))
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if not event:
        raise NotFoundError("event not found")
    return event


async def get_next_occurrence(event_id: int, db: AsyncSession) -> EventOccurrence:
    stmt = (select(EventOccurrence)
            .where(EventOccurrence.event_id == event_id)
            .where(EventOccurrence.occurrence_date >= date.today())
            .order_by(EventOccurrence.occurrence_date.asc())
            .limit(1))
    result = await db.execute(stmt)
    occurrence = result.scalar_one_or_none()
    return occurrence


async def get_event_list(user: User, db: AsyncSession, with_occurrence: bool = False) -> Sequence[Event]:
    stmt = (select(Event)
            .where(Event.deleted_at == None))
    if with_occurrence:
        stmt = stmt.options(selectinload(Event.occurrences))
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))
    result = await db.execute(stmt)
    events = result.scalars().all()
    return events