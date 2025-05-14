from typing import List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.core.models.mixins import TimestampMixin, SurrogatePKMixin, GUID
from app.core.models.base import Base
from app.core.enums import UserRole

if TYPE_CHECKING:
    from .recipient import Recipient
    from .event import Event
    from .idea import GiftIdea
    from .media import MediaFile


class User(SurrogatePKMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __mapper_args__ = {
        "polymorphic_on": "role",
    }

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default=UserRole.USER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    bio: Mapped[str] = mapped_column(String, nullable=True)

    ava_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("media_files.id"), nullable=True)

    avatar: Mapped["MediaFile"] = relationship(
        "MediaFile",
    )
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="user",
    )
    ideas: Mapped[List["GiftIdea"]] = relationship(
        "GiftIdea",
        back_populates="user",
    )

    @validates("role")
    def validate_role(self, key, value):
        if isinstance(value, UserRole):
            return value.value
        elif isinstance(value, str):
            if value not in UserRole.__members__:
                raise ValueError(f"Invalid role: {value}")
            return value
        else:
            raise TypeError(f"Role must be str or UserRole, got {type(value)}")


class SimpleUser(User):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.USER.value,
    }

    recipients: Mapped[List["Recipient"]] = relationship(
        "Recipient",
        back_populates="user",
    )


class AdminUser(User):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.ADMIN.value,
    }


class RootUser(AdminUser):
    __mapper_args__ = {
        "polymorphic_identity": UserRole.ROOT.value,
    }