from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import mapped_column, Mapped, validates

from app.core.enums import MediaType
from app.core.models.base import Base
from app.core.models.mixins import SurrogatePKMixin, TimestampMixin


class MediaFile(SurrogatePKMixin, TimestampMixin, Base):
    __tablename__ = "media_files"

    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    alt: Mapped[str] = mapped_column(String(64), nullable=True)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    ratio: Mapped[float] = mapped_column(Float, nullable=False)

    @validates("type")
    def validate_role(self, key, value):
        if isinstance(value, MediaType):
            return value.value
        elif isinstance(value, str):
            if value not in MediaType.__members__:
                raise ValueError(f"Invalid type: {value}")
            return value
        else:
            raise TypeError(f"Type must be str or MediaType, got {type(value)}")
