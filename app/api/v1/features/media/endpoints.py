from typing import List

from fastapi import APIRouter, UploadFile, status, Depends

from app.core.enums import MediaType
from app.repositories.orm.media import MediaRepository
from app.schemas.media import MediaFileMeta, MediaFileRead
from app.storage import S3MediaStorage
from app.service.media import MediaUploaderService, AvaMediaValidator, ContentMediaValidator
from app.api.v1.dependencies import DBSessionDepends
from .dependencies import extract_image_data, extract_images_data


router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload/avatar", status_code=status.HTTP_201_CREATED, response_model=MediaFileRead)
async def upload_ava(
        db: DBSessionDepends,
        file: UploadFile,
        extracted: tuple[MediaFileMeta, bytes] = Depends(extract_image_data),
):
    """upload ava for user or recipient"""
    data, file_bytes = extracted

    uploader = MediaUploaderService(MediaRepository(db), S3MediaStorage(), AvaMediaValidator())
    media = await uploader.upload_one(file_bytes, data, MediaType.AVATAR)

    return media


@router.post("/upload/content", status_code=status.HTTP_201_CREATED, response_model=List[MediaFileRead])
async def upload_content(
        db: DBSessionDepends,
        files: List[UploadFile],
        extracted_list: tuple[List[MediaFileMeta], List[bytes]] = Depends(extract_images_data),
):
    """upload media for idea or gifts"""
    datas, file_bytes_list = extracted_list

    uploader = MediaUploaderService(MediaRepository(db), S3MediaStorage(), ContentMediaValidator())
    media = await uploader.upload_many(file_bytes_list, datas, MediaType.CONTENT)
    return media
