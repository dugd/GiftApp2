from typing import TYPE_CHECKING, List, Optional
from datetime import date
from enum import Enum
from uuid import UUID

from sqlalchemy import Integer, String, Date, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.core.models.base import Base
from app.core.models.mixins import GUID, SurrogatePKMixin, TimestampMixin, SoftDeleteMixin


if TYPE_CHECKING:
    from .auth import User
    from .recipient import Recipient

class EventType(Enum):
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    HOLIDAY = "HOLIDAY"
    OTHER = "OTHER"


class Event(SurrogatePKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "(NOT is_global) OR (recipient_id IS NULL)",
            name="global_recipient_null",
        ),
    )

    title: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default=EventType.OTHER.value)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_repeating: Mapped[bool] = mapped_column(Boolean, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    user_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=True)
    recipient_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("recipients.id"), nullable=True)


    related_recipient: Mapped["Recipient"] = relationship(
        "Recipient",
        back_populates="related_events"
    )
    occurrences: Mapped[List["EventOccurrence"]] = relationship(
        "EventOccurrence",
        back_populates="event",
    )
    last_occurrence: Mapped[Optional["EventOccurrence"]] = relationship(
        "EventOccurrence",
        viewonly=True,
        order_by="desc(EventOccurrence.occurrence_date)",
        uselist=False,
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="events",
    )

    @validates("type")
    def validate_type(self, key, value):
        if isinstance(value, EventType):
            return value.value
        elif isinstance(value, str):
            if value not in EventType.__members__:
                raise ValueError(f"Invalid type: {value}")
            return value
        else:
            raise TypeError(f"Type must be str or EventType, got {type(value)}")


class EventOccurrence(SurrogatePKMixin, TimestampMixin, Base):
    __tablename__ = "event_occurrences"

    occurrence_date: Mapped[date] = mapped_column(Date, nullable=False)

    event_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("events.id"), nullable=False)

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="occurrences",
    )

