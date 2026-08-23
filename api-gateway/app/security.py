from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2."""
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return _password_hash.verify(password, hashed)


def create_access_token(user_id: UUID, role: str) -> str:
    """Create a signed JWT carrying the user id and role."""
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "role": role, "exp": expires}
    return jwt.encode(
        payload, settings.proxy_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT. Raises jwt.PyJWTError when invalid or expired."""
    settings = get_settings()
    return jwt.decode(
        token, settings.proxy_secret_key, algorithms=[settings.jwt_algorithm]
    )
