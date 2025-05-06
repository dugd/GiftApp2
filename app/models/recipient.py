from datetime import date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON

from app.core.models.base import Base
from app.core.models.mixins import GUID, SurrogatePKMixin


if TYPE_CHECKING:
    from .auth import SimpleUser
    from .event import Event


class Recipient(SurrogatePKMixin, Base):
    __tablename__ = "recipients"

    name: Mapped[str] = mapped_column(String(32), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    relation: Mapped[str] = mapped_column(String(32), nullable=True)
    preferences: Mapped[Optional[List[str]]] = mapped_column(MutableList.as_mutable(JSON), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)

    related_events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="related_recipient"
    )
    user: Mapped["SimpleUser"] = relationship(
        "SimpleUser",
        back_populates="recipients",
    )
