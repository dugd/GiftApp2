from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.core.models.mixins import TimestampMixin, SurrogatePKMixin
from app.core.models.base import Base


if TYPE_CHECKING:
    from .recipient import Recipient
    from .event import Event
    from .idea import GiftIdea


class UserRole(Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USER = "USER"


class User(SurrogatePKMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __mapper_args__ = {
        "polymorphic_on": "role",
    }

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default=UserRole.USER.value)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

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