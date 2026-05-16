import pytest
from uuid import uuid4
from core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hashing():
    password = "SecurePass123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass", hashed)


def test_jwt_roundtrip():
    user_id = uuid4()
    email = "test@example.com"
    token = create_access_token(user_id, email)
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["type"] == "access"
