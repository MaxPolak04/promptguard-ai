from app.config import Settings


def test_database_url_assembled_from_components():
    settings = Settings(
        postgres_user="u",
        postgres_password="p",
        postgres_host="h",
        postgres_port=5432,
        postgres_db="d",
    )
    assert settings.database_url == "postgresql+asyncpg://u:p@h:5432/d"
