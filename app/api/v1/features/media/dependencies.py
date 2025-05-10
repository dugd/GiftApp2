from io import BytesIO

from fastapi import UploadFile, HTTPException, status
from PIL import Image, UnidentifiedImageError

from app.utils.media import calculate_hash
from app.schemas.media import MediaFileData


ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024


async def extract_image_data(file: UploadFile) -> MediaFileData:
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
    except UnidentifiedImageError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    width, height = image.size
    ratio = width / height

    file_hash = calculate_hash(file_bytes)

    return MediaFileData(
        filename=filename,
        mime_type=content_type,
        size_bytes=size_bytes,
        width=width,
        height=height,
        ratio=ratio,
        hash=file_hash,
    )