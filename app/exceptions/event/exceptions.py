from datetime import date
from app.exceptions.exceptions import GiftAppError


class PastEventError(GiftAppError):
    def __init__(self, now: date):
        super().__init__(f"Event cannot be created before {str(now)}", status_code=400)
