from abc import ABC, abstractmethod
from io import BytesIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


class MediaStorage(ABC):
    @abstractmethod
    def upload(self, file: bytes, path: str, content_type: str) -> str:
        pass

    @abstractmethod
    def delete(self, path: str):
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


class S3MediaStorage(MediaStorage):
    def __init__(self):
        self.s3_client = s3_client

    def upload(self, file: bytes, path: str, content_type: str) -> str:
        try:
            file_like = BytesIO(file)
            self.s3_client.upload_fileobj(
                file_like,
                settings.AWS_BUCKET_NAME,
                path,
                ExtraArgs={
                    "ContentType": content_type,
                }
            )
            return f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{path}"
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Error uploading file: {e}")

    def delete(self, path: str):
        raise NotImplementedError()

    def exists(self, path: str) -> bool:
        raise NotImplementedError()