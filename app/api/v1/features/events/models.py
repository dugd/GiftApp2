from typing import TYPE_CHECKING, List, Optional
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Integer, String, Date, TIMESTAMP, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.api.v1.features.models import User, Recipient

class EventType(Enum):
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    HOLIDAY = "HOLIDAY"
    OTHER = "OTHER"


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "(NOT is_global) OR (recipient_id IS NULL)",
            name="chk_global_recipient_null",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default=EventType.OTHER.value)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_repeating: Mapped[bool] = mapped_column(Boolean, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipients.id"), nullable=True)


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

    def soft_delete(self):
        self.deleted_at = func.now()

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


class EventOccurrence(Base):
    __tablename__ = "event_occurrences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    occurrence_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), nullable=False)

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="occurrences",
    )

