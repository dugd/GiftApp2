from app.exceptions.exceptions import GiftAppError


class WrongCredentials(GiftAppError):
    def __init__(self):
        super().__init__("Incorrect credentials", status_code=401)


class EmailAlreadyTaken(GiftAppError):
    def __init__(self, email: str):
        super().__init__(f"email '{email}' is already taken", status_code=409)