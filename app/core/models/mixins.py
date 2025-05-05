from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import TIMESTAMP


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        onupdate=func.now(),
        nullable=True,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=True,
    )

    def soft_delete(self):
        self.deleted_at = func.now()