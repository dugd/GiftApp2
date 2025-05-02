from app.api.v1.features.exceptions import GiftAppError


class WrongCredentials(GiftAppError):
    pass


class EmailAlreadyTaken(GiftAppError):
    pass