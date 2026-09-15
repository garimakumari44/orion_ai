"""
app/db/database.py

Database configuration and SQLAlchemy infrastructure.

Responsibilities
----------------
- Define the declarative ORM Base.
- Create the async SQLAlchemy engine.
- Create the async session factory.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """

    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)