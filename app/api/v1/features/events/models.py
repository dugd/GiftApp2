from datetime import date, datetime
from enum import Enum

from sqlalchemy import Integer, String, Date, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.models.base import Base


class EventType(Enum):
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    HOLIDAY = "HOLIDAY"
    OTHER = "OTHER"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False, default=EventType.OTHER.value)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_repeating: Mapped[bool] = mapped_column(Boolean, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipients.id"), nullable=True)

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

    # it is bad when set user_id before is_global
    @validates("user_id")
    def not_null_if_local(self, key, value):
        if not self.is_global and value is None:
            raise ValueError(f"user_id is required for local events")
        return value


class EventOccurrence(Base):
    __tablename__ = "event_occurrences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    occurrence_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), nullable=False)

