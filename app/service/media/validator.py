from abc import ABC, abstractmethod

from app.exceptions.media.exceptions import MediaValidateFailure
from app.schemas.media import MediaFileData


class BaseMediaValidator(ABC):
    @abstractmethod
    def validate(self, media_data: MediaFileData) -> bool:
        pass


class AvaMediaValidator(BaseMediaValidator):
    def validate(self, media_data: MediaFileData) -> bool:
        if media_data.width != media_data.height:
            raise MediaValidateFailure("Avatar height and width must be equal")
        return True


class ContentMediaValidator(BaseMediaValidator):
    def validate(self, media_data: MediaFileData) -> bool:
        if 0.5 > media_data.ratio > 2:
            raise MediaValidateFailure("ratio must be between 0.5 and 2")
        return True
