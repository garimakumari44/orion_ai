"""
app/db/session.py

FastAPI database session dependency.

Provides a request-scoped AsyncSession and guarantees
that the session is closed after the request completes.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async SQLAlchemy session to FastAPI dependencies.
    """

    async with AsyncSessionLocal() as session:
        yield session