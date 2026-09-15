from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional


class ExpirationPolicy(ABC):
    """
    Base expiration policy.

    Determines when a memory expires.
    """

    @abstractmethod
    def expiration_time(
        self,
        *,
        memory_type: str,
        importance: float,
        created_at: Optional[datetime] = None,
    ) -> Optional[datetime]:
        """
        Return expiration datetime.

        Returning None means memory never expires.
        """
        raise NotImplementedError


class TTLExpirationPolicy(ExpirationPolicy):
    """
    Time-to-live expiration policy.

    Higher importance memories survive longer.

    Example:

    temporary     -> hours
    working       -> days
    conversation  -> weeks
    research      -> permanent
    preference    -> permanent
    """

    def expiration_time(
        self,
        *,
        memory_type: str,
        importance: float,
        created_at: Optional[datetime] = None,
    ) -> Optional[datetime]:

        created_at = created_at or datetime.utcnow()

        # Permanent memories

        if memory_type in {
            "research",
            "preference",
            "fact",
        }:
            return None

        if importance >= 0.95:
            return None

        if memory_type == "temporary":
            ttl = timedelta(hours=12)

        elif memory_type == "working":
            ttl = timedelta(days=2)

        elif memory_type == "conversation":
            ttl = timedelta(days=30)

        elif memory_type == "project":
            ttl = timedelta(days=180)

        else:
            ttl = timedelta(days=14)

        ttl *= (1.0 + importance)

        return created_at + ttl

    @staticmethod
    def is_expired(
        expiration: Optional[datetime],
        now: Optional[datetime] = None,
    ) -> bool:
        """
        Check whether a memory has expired.
        """

        if expiration is None:
            return False

        now = now or datetime.utcnow()

        return now >= expiration