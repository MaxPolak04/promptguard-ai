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
        json={"email": "short@example.com", "password": "short"},
    )
    assert resp.status_code == 422
