import pytest
from pydantic import ValidationError

from app.config import Settings

_VALID_SECRET = "test-secret-key-not-for-production-use"  # pragma: allowlist secret


def test_database_url_assembled_from_components():
    settings = Settings(
        postgres_user="u",
        postgres_password="p",
        postgres_host="h",
        postgres_port=5432,
        postgres_db="d",
    )
    assert settings.database_url == "postgresql+asyncpg://u:p@h:5432/d"


def test_auth_settings_defaults():
    settings = Settings(
        postgres_user="u",
        postgres_password="p",
        postgres_db="d",
        proxy_secret_key=_VALID_SECRET,
    )
    assert settings.proxy_secret_key == _VALID_SECRET
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30


def test_short_proxy_secret_key_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            postgres_user="u",
            postgres_password="p",
            postgres_db="d",
            proxy_secret_key="short",  # pragma: allowlist secret
        )
