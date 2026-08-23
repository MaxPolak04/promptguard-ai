from sqlalchemy import select

from app.models import User
from app.security import decode_access_token


async def test_register_creates_user(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "chat_user"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data


async def test_register_duplicate_email_returns_409(client):
    body = {"email": "dup@example.com", "password": "secret123"}
    first = await client.post("/auth/register", json=body)
    assert first.status_code == 201
    second = await client.post("/auth/register", json=body)
    assert second.status_code == 409


async def test_register_rejects_short_password(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "pw123"},
    )
    assert resp.status_code == 422
    assert "pw123" not in resp.text
    assert "[redacted]" in resp.text


async def test_register_invalid_email_keeps_input_visible(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert resp.status_code == 422
    assert "not-an-email" in resp.text


async def _register(client, email="login@example.com", password="secret123"):
    resp = await client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert resp.status_code == 201
    return resp.json()


async def test_login_returns_valid_token(client):
    created = await _register(client)
    resp = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    payload = decode_access_token(data["access_token"])
    assert payload["sub"] == created["id"]
    assert payload["role"] == "chat_user"


async def test_login_wrong_password_returns_401(client):
    await _register(client)
    resp = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(client):
    resp = await client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "secret123"},
    )
    assert resp.status_code == 401


async def test_login_inactive_user_returns_401(app, client):
    await _register(client, email="inactive@example.com")
    maker = app.state.sessionmaker
    async with maker() as session:
        result = await session.execute(
            select(User).where(User.email == "inactive@example.com")
        )
        user = result.scalar_one()
        user.is_active = False
        await session.commit()
    resp = await client.post(
        "/auth/login",
        json={"email": "inactive@example.com", "password": "secret123"},
    )
    assert resp.status_code == 401
