class GiftAppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class NotFoundError(GiftAppError):
    def __init__(self, entity: str):
        super().__init__(f"{entity} not found", status_code=404)
