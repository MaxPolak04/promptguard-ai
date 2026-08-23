import uuid

import jwt
import pytest

from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("s3cret-password")
    assert hashed != "s3cret-password"
    assert verify_password("s3cret-password", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_roundtrip_carries_subject_and_role():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "chat_user")
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "chat_user"
    assert "exp" in payload


def test_tampered_token_is_rejected():
    token = create_access_token(uuid.uuid4(), "chat_user")
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(token + "x")
