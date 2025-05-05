from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import func, Dialect
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TIMESTAMP, TypeDecorator, CHAR


class GUID(TypeDecorator):
    impl = CHAR

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect: Dialect):
        if value is None or dialect.name == "postgresql":
            return value
        else:
            if not isinstance(value, UUID):
                value = UUID(value)
            return value.hex

    def process_result_value(
        self, value, dialect: Dialect
    ):
        if value is None:
            return value
        else:
            if not isinstance(value, UUID):
                value = UUID(value)
            return value


class SurrogatePKMixin:
    id: Mapped[UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid4,
    )


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