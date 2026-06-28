from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db import build_engine, build_sessionmaker
from app.models import Base
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the engine and create tables on startup, dispose on shutdown."""
    settings = get_settings()
    engine = build_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.engine = engine
    app.state.sessionmaker = build_sessionmaker(engine)
    try:
        yield
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="PromptGuard API Gateway", lifespan=lifespan)
    app.include_router(health.router)
    return app


app = create_app()
