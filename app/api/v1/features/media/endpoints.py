from typing import List

from fastapi import APIRouter, UploadFile, status, Depends

from app.models import MediaType
from app.repositories.media import MediaRepository
from app.schemas.media import MediaFileData
from app.storage import S3MediaStorage
from app.service.media import MediaUploaderService, AvaMediaValidator, ContentMediaValidator
from app.api.v1.dependencies import DBSessionDepends
from app.api.v1.features.media.dependencies import extract_image_data


router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload/avatar", status_code=status.HTTP_201_CREATED)
async def upload_ava(
        db: DBSessionDepends,
        file: UploadFile,
        data: MediaFileData = Depends(extract_image_data),
):
    """upload ava for user or recipient"""
    file_bytes = await file.read()

    uploader = MediaUploaderService(MediaRepository(db), S3MediaStorage(), AvaMediaValidator())
    media = await uploader.upload_one(file_bytes, data, MediaType.AVATAR)

    return media


@router.post("/upload/content", status_code=status.HTTP_201_CREATED)
async def upload_content(
        db: DBSessionDepends,
        files: List[UploadFile],
):
    """upload media for idea or gifts"""
    datas = [await extract_image_data(file) for file in files]
    file_bytes_list = [await file.read() for file in files]

    uploader = MediaUploaderService(MediaRepository(db), S3MediaStorage(), ContentMediaValidator())
    media = await uploader.upload_many(file_bytes_list, datas, MediaType.CONTENT)
    return media
