from datetime import timedelta

from jose.exceptions import JWTError, ExpiredSignatureError
import pytest

from app.api.v1.features.auth.security import hash_password, verify_password, create_jwt_token, decode_token


def test_password_hashing_and_verification():
    raw = "my-secret"

    hashed = hash_password(raw)

    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_token_creation_and_decode():
    init_payload = {
        "id": 5,
        "sub": "some@example.com",
    }

    jwt = create_jwt_token(init_payload, timedelta(minutes=15))
    token_payload = decode_token(jwt)

    assert token_payload["id"] == init_payload["id"]
    assert token_payload["sub"] == init_payload["sub"]


def test_invalid__jwt_token_error():
    invalid_token = "this.is.not.a.valid.token"

    with pytest.raises(JWTError):
        decode_token(invalid_token)


def test_expired_jwt_token_error():
    payload = {
        "id": 1,
        "sub": "test@example.com"
    }

    expired_token = create_jwt_token(payload, timedelta(seconds=-1))

    with pytest.raises(ExpiredSignatureError):
        decode_token(expired_token)