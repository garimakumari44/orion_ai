"""
Generic transaction support for the storage layer.

Backends that support ACID transactions (e.g. PostgreSQL, MongoDB)
can override commit/rollback.

Backends without transaction support (e.g. Qdrant) simply no-op.
"""

from __future__ import annotations

from abc import ABC
from typing import Any


class StorageTransaction(ABC):
    """
    Base transaction object.

    Can be used as:

        with transaction:
            ...
    """

    def __init__(self, connection: Any = None):
        self.connection = connection
        self.active = False

    def begin(self) -> None:
        """Start transaction."""
        self.active = True

    def commit(self) -> None:
        """Commit transaction."""
        self.active = False

    def rollback(self) -> None:
        """Rollback transaction."""
        self.active = False

    def close(self) -> None:
        """Close resources."""
        self.connection = None
        self.active = False

    def __enter__(self) -> "StorageTransaction":
        self.begin()
        return self

    def __exit__(self, exc_type, exc, tb):

        if exc_type:
            self.rollback()
        else:
            self.commit()

        self.close()

        return False