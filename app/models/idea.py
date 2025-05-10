from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Boolean, Numeric, JSON, TIMESTAMP
from sqlalchemy.ext.mutable import MutableList

from app.core.models.base import Base
from app.core.models.mixins import GUID, SurrogatePKMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .auth import User


class GiftIdea(SurrogatePKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "gift_ideas"

    title: Mapped[str] = mapped_column(String(64), nullable=False)
    tags: Mapped[Optional[List[str]]] = mapped_column(MutableList.as_mutable(JSON), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    view_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estimated_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    def archive(self):
        self.archived_at = func.now()

    user_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=True)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="ideas",
    )