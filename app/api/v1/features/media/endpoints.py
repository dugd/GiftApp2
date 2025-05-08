from typing import List
from io import BytesIO

from PIL import Image
from fastapi import APIRouter, UploadFile

from app.api.v1.features.media.utils import verify_file_size, verify_aspect_equal, verify_image_mime

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload/avatar")
async def upload(file: UploadFile):
    """upload ava for user or recipient"""
    await verify_image_mime(file)

    file_bytes = await file.read()
    await verify_file_size(file_bytes)

    image = Image.open(BytesIO(file_bytes))
    await verify_aspect_equal(image)

    return {"status": "ok", "mime": file.content_type}


@router.post("/upload/content")
async def upload(files: List[UploadFile]):
    """upload media for idea or gifts (ratio < 1.5)"""
    pass
