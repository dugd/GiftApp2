from fastapi import HTTPException, status, UploadFile

from PIL import Image

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024


async def verify_image_mime(file: UploadFile):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image MIME type")
    return file


async def verify_file_size(file_bytes: bytes):
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    return file_bytes


async def verify_aspect_equal(image: Image.Image):
    if image.width != image.height:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Width != height")
    return image
