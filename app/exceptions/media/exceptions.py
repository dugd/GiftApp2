from app.exceptions.exceptions import GiftAppError


class MediaValidateFailure(GiftAppError):
    def __init__(self, message: str):
        super().__init__(message, 400)
