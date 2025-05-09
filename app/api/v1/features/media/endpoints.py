from typing import List
from io import BytesIO

from PIL import Image
from fastapi import APIRouter, UploadFile, HTTPException, status

from app.utils.media import calculate_hash


ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024


async def extract_image_data(file: UploadFile):
    filename = file.filename
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)
    if size_bytes > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    file_bytes = await file.read()
    file.file.seek(0)

    try:
        image = Image.open(BytesIO(file_bytes))
        image.verify()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    width, height = image.size
    ratio = width / height

    file_hash = calculate_hash(file_bytes)

    return {
        "file_name": filename,
        "mime_type": content_type,
        "size_bytes": size_bytes,
        "width": width,
        "height": height,
        "aspect_ratio": round(ratio, 3),
        "hash": file_hash,
    }


def validate_avatar_data(data: dict) -> bool:
    if data["width"] != data["height"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar height and width must be equal")
    return True


def validate_content_data(data: dict) -> bool:
    if 0.5 > data["aspect_ratio"] > 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ratio must be between 0.5 and 2")
    return True


router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload/avatar")
async def upload_ava(file: UploadFile):
    """upload ava for user or recipient"""
    data = await extract_image_data(file)
    validate_avatar_data(data)

    return data


@router.post("/upload/content")
async def upload_content(files: List[UploadFile]):
    """upload media for idea or gifts"""
    datas = [await extract_image_data(file) for file in files]
    for data in datas:
        validate_content_data(data)
    return datas
