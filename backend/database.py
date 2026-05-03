"""
database.py
-----------
SQLAlchemy async engine + session factory.
Connection string is read from the DATABASE_URL environment variable.

For local dev (no Docker): set DATABASE_URL in a .env file.
For Docker Compose: injected automatically via environment block.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

import ssl

_ssl_ctx = ssl.create_default_context()

engine = create_async_engine(
    settings.database_url.split("?")[0],  # strip all query params from URL
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={"ssl": _ssl_ctx},
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables. Called at startup if not using Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)