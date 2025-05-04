from typing import List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.core.base import Base


if TYPE_CHECKING:
    from .recipients import Recipient
    from .events import Event


class UserRole(Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {
        "polymorphic_on": "role",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default=UserRole.USER.value)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    events: Mapped[List["Event"]] = relationship(
        "Event",
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