from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.models.base import Base


class UserRole(Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default=UserRole.USER.value)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

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