import pytest

from app.api.v1.features.auth.security import hash_password, verify_password


def test_password_hashing_and_verification():
    raw = "my-secret"

    hashed = hash_password(raw)

    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong-password", hashed) is False