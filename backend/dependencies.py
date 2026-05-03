"""
dependencies.py
---------------
FastAPI dependency for async DB sessions.
Yields one session per request and commits/rolls back automatically.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise