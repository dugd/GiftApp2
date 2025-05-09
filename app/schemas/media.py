from pydantic import BaseModel


class MediaFileData(BaseModel):
    filename: str
    mime_type: str
    size_bytes: int
    width: int
    height: int
    ratio: float
    hash: str