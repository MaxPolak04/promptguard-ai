import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.models import Base


@pytest_asyncio.fixture
async def app():
    """A FastAPI app wired to a fresh in-memory SQLite database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    application = create_app()
    application.state.engine = engine
    application.state.sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    yield application
    await engine.dispose()


@pytest_asyncio.fixture
async def client(app):
    """An HTTP client bound to the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
