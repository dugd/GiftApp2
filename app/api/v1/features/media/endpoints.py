from typing import List

from fastapi import APIRouter, UploadFile

from app.s3_service import upload_file


router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload/avatar")
async def upload(file: UploadFile):
    """upload ava for user or recipient (width == height)"""
    pass


@router.post("/upload/content")
async def upload(files: List[UploadFile]):
    """upload media for idea or gifts (ratio < 1.5)"""
    pass
