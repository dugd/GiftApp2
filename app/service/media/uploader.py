from typing import List
import os
import base64

from fastapi.concurrency import run_in_threadpool

from app.storage import MediaStorage
from app.schemas.media import MediaFileData
from app.service.media.validator import BaseMediaValidator
from app.models import MediaFile, MediaType
from app.repositories.media import MediaRepository


class MediaUploaderService:
    """
    A service for handling media file uploads.

    This service provides functionality for uploading media files while ensuring
    validation, checking for duplicates, and managing media file storage. It validates
    the supplied media data, checks if the media already exists using its hash, handles
    the upload of the file to a specified storage service, and persists media details
    to a repository, avoiding redundant entries.

    :ivar repo: Media repository instance for managing media file records.
    :type repo: MediaRepository
    :ivar storage: Media storage instance for storing and retrieving media files.
    :type storage: MediaStorage
    :ivar validator: Validator instance to verify media data before upload.
    :type validator: BaseMediaValidator
    """
    def __init__(self, repo: MediaRepository, storage: MediaStorage, validator: BaseMediaValidator):
        self.repo = repo
        self.storage = storage
        self.validator = validator

    async def upload_one(
            self,
            file_bytes: bytes,
            media_data: MediaFileData,
            _type: MediaType
    ) -> MediaFile:
        self.validator.validate(media_data)

        existing_media = await self.repo.get_by_hash(media_data.hash)
        if existing_media:
            return existing_media

        _, ext = os.path.splitext(media_data.filename)
        decoded_hash = base64.urlsafe_b64encode(bytes.fromhex(media_data.hash)).rstrip(b"=").decode()
        upload_path = f"{_type.value.lower()}/{decoded_hash}{ext}"

        url = await run_in_threadpool(self.storage.upload, file_bytes, upload_path, media_data.mime_type)

        media = MediaFile(
            url=url,
            hash=media_data.hash,
            type=MediaType.AVATAR.value,
            alt=media_data.filename,
            mime_type=media_data.mime_type,
            size=media_data.size_bytes,
            width=media_data.width,
            height=media_data.height,
            ratio=media_data.ratio,
        )
        await self.repo.add(media)

        return media

    async def upload_many(
            self,
            files: List[bytes],
            datas: List[MediaFileData],
            _type: MediaType
    ) -> List[MediaFile]:
        results: List[MediaFile] = []
        uploaded_paths: List[str] = []

        try:
            for file_bytes, media_data in zip(files, datas):
                self.validator.validate(media_data)

                existing_media = await self.repo.get_by_hash(media_data.hash)
                if existing_media:
                    results.append(existing_media)
                    continue

                _, ext = os.path.splitext(media_data.filename)
                decoded_hash = base64.urlsafe_b64encode(bytes.fromhex(media_data.hash)).rstrip(b"=").decode()
                upload_path = f"{_type.value.lower()}/{decoded_hash}{ext}"

                url = await run_in_threadpool(self.storage.upload, file_bytes, upload_path, media_data.mime_type)
                uploaded_paths.append(upload_path)

                media = MediaFile(
                    url=url,
                    hash=media_data.hash,
                    type=_type.value,
                    alt=media_data.filename,
                    mime_type=media_data.mime_type,
                    size=media_data.size_bytes,
                    width=media_data.width,
                    height=media_data.height,
                    ratio=media_data.ratio,
                )
                results.append(media)

            results = await self.repo.add_many(results)
            return results
        except RuntimeError as e:
            for path in uploaded_paths:
                await run_in_threadpool(self.storage.delete, path)
            raise e
