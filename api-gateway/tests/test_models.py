import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.models import Base, User, UserRole


@pytest_asyncio.fixture
async def session():
    """Provide a session bound to a fresh in-memory SQLite database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as db_session:
        yield db_session
    await engine.dispose()


async def test_create_user_and_read_back(session: AsyncSession):
    user = User(email="alice@example.com", hashed_password="hashed")
    session.add(user)
    await session.commit()

    result = await session.execute(
        select(User).where(User.email == "alice@example.com")
    )
    fetched = result.scalar_one()
    assert fetched.email == "alice@example.com"
    assert isinstance(fetched.id, uuid.UUID)


async def test_user_defaults(session: AsyncSession):
    user = User(email="bob@example.com", hashed_password="hashed")
    session.add(user)
    await session.commit()

    result = await session.execute(select(User).where(User.email == "bob@example.com"))
    fetched = result.scalar_one()
    assert fetched.role == UserRole.chat_user
    assert fetched.is_active is True
    assert isinstance(fetched.created_at, datetime)


async def test_email_must_be_unique(session: AsyncSession):
    session.add(
        User(
            email="dup@example.com",
            hashed_password="h1",  # pragma: allowlist secret
        )
    )
    await session.commit()

    session.add(
        User(
            email="dup@example.com",
            hashed_password="h2",  # pragma: allowlist secret
        )
    )
    with pytest.raises(IntegrityError):
        await session.commit()
