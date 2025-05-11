from datetime import date

from .common import GiftAppError


class PastEventError(GiftAppError):
    def __init__(self, now: date):
        super().__init__(f"Event cannot be created before {str(now)}", status_code=400)
