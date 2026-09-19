"""
Redis Adapter

Responsibilities
----------------
- Key-value storage
- Cache operations
- TTL management
- Pub/Sub support
"""

from __future__ import annotations

from typing import Any

import redis


class RedisAdapter:
    """
    Thin wrapper around redis-py.
    """

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        decode_responses: bool = False,
    ):
        self.client = redis.Redis.from_url(
            url,
            decode_responses=decode_responses,
        )

    def get(self, key: str) -> Any:
        return self.client.get(key)

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        return self.client.set(
            key,
            value,
            ex=ttl,
        )

    def delete(self, *keys: str) -> int:
        return self.client.delete(*keys)

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def expire(
        self,
        key: str,
        ttl: int,
    ) -> bool:
        return self.client.expire(key, ttl)

    def increment(
        self,
        key: str,
        amount: int = 1,
    ) -> int:
        return self.client.incr(key, amount)

    def publish(
        self,
        channel: str,
        message: str,
    ) -> int:
        return self.client.publish(channel, message)

    def health(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False