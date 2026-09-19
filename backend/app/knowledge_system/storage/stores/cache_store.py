from __future__ import annotations

import time

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CacheStore(ABC):
    """
    Abstract cache interface.

    Can be implemented by:
    - Redis
    - Memcached
    - In-Memory
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Return cached value or None."""
        ...

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Store value with optional TTL (seconds)."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete one cache entry."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...

    @abstractmethod
    async def clear(self) -> None:
        """Clear entire cache."""
        ...