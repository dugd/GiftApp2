from datetime import date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON
from app.core.base import Base

if TYPE_CHECKING:
    from .auth import SimpleUser
    from .events import Event


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    relation: Mapped[str] = mapped_column(String(32), nullable=True)
    preferences: Mapped[Optional[List[str]]] = mapped_column(MutableList.as_mutable(JSON), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    related_events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="related_recipient"
    )
    user: Mapped["SimpleUser"] = relationship(
        "SimpleUser",
        back_populates="recipients",
    )
