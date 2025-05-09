from fastapi.concurrency import run_in_threadpool

from app.schemas.media import MediaFileData
from app.storage import MediaStorage
from app.service.media.validator import BaseMediaValidator


class MediaUploaderService:
    def __init__(self, storage: MediaStorage, validator: BaseMediaValidator):
        self.storage = storage
        self.validator = validator

    async def upload_one(self, file_bytes: bytes, media_data: MediaFileData) -> MediaFileData:
        self.validator.validate(media_data)
        await run_in_threadpool(self.storage.upload, file_bytes, media_data.filename, media_data.mime_type)
        return media_data

