import bcrypt
from jose import jwt
from datetime import datetime, timedelta

from app.core.enums import TokenType
from app.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    password_bytes = password.encode("UTF-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("UTF-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("UTF-8"), hashed_password.encode("UTF-8"))


def create_jwt_token(payload: dict, expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


_EXPIRES_DELTAS = {
    TokenType.access: timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    TokenType.refresh: timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    TokenType.activation: timedelta(hours=settings.ACTIVATION_TOKEN_EXPIRE_HOURS),
}


def create_token(payload: dict, token_type: TokenType) -> str:
    return create_jwt_token(payload, _EXPIRES_DELTAS[token_type])


def decode_token(token: str):
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "type"]},
    )
    return payload
