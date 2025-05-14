from .common import GiftAppError


class WrongCredentials(GiftAppError):
    def __init__(self):
        super().__init__("Incorrect credentials", status_code=401)


class EmailAlreadyTaken(GiftAppError):
    def __init__(self, email: str):
        super().__init__(f"email '{email}' is already taken", status_code=409)


class UsernameAlreadyTaken(GiftAppError):
    def __init__(self, username: str):
        super().__init__(f"username '{username}' is already taken", status_code=409)


class UserAlreadyActivated(GiftAppError):
    def __init__(self, username: str):
        super().__init__(f"user '{username}' is already activated", status_code=409)


class UserIsNotActivated(GiftAppError):
    def __init__(self, username: str):
        super().__init__(f"user '{username}' is not activated", status_code=401)