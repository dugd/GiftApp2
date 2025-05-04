from app.api.v1.exceptions import GiftAppError


class WrongCredentials(GiftAppError):
    pass


class EmailAlreadyTaken(GiftAppError):
    pass