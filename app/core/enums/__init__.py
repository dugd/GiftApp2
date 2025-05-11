from enum import Enum


class EventType(Enum):
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    HOLIDAY = "HOLIDAY"
    OTHER = "OTHER"


class MediaType(Enum):
    AVATAR = "AVATAR"
    CONTENT = "CONTENT"


class UserRole(Enum):
    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USER = "USER"
