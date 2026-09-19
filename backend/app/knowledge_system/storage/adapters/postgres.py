"""
PostgreSQL Adapter

Thin wrapper around SQLAlchemy.

Responsibilities
----------------
- CRUD operations
- Transactions
- Session management
- Bulk inserts
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class PostgresAdapter:
    """
    Generic PostgreSQL adapter.
    """

    def __init__(
        self,
        database_url: str,
        *,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
    ):
        self.engine = create_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            future=True,
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @contextmanager
    def session(self):
        session: Session = self.SessionLocal()

        try:
            yield session
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def add(self, obj: Any):

        with self.session() as session:
            session.add(obj)

    def add_all(self, objects: Iterable[Any]):

        with self.session() as session:
            session.add_all(list(objects))

    def delete(self, obj: Any):

        with self.session() as session:
            session.delete(obj)

    def merge(self, obj: Any):

        with self.session() as session:
            session.merge(obj)

    def execute(self, statement):

        with self.session() as session:
            return session.execute(statement)

    def health(self) -> bool:
        try:
            with self.engine.connect():
                return True
        except Exception:
            return False