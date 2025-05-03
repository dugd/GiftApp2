from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.sql import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.features.exceptions import NotFoundError
from app.api.v1.features.events.exceptions import PastEventError
from app.api.v1.features.events.models import Event, EventOccurrence
from app.api.v1.features.events.schemas import EventCreate, EventModel, EventUpdate
from app.api.v1.features.auth.models import User, SimpleUser
from app.core.database import async_session


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


async def event_update_info(event: Event, data: EventUpdate, db: AsyncSession) -> Event:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    await db.commit()

    return event


async def event_delete(event: Event, db: AsyncSession):
    event.soft_delete()
    await db.commit()


async def get_event(event_id: int, user: User, db: AsyncSession) -> Event:
    stmt = select(Event).where(Event.id == event_id).where(Event.deleted_at == None)
    if isinstance(user, SimpleUser):
        stmt = stmt.where(or_(Event.user_id == user.id, Event.is_global))
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if not event:
        raise NotFoundError("event not found")
    return event


async def get_event_list(user: User, db: AsyncSession) -> Event:
    pass