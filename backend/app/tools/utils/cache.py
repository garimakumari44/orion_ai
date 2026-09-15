import time
import asyncio
from typing import Any, Optional


class CacheItem:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expiry = time.time() + ttl


    def expired(self):
        return time.time() > self.expiry



class MemoryCache:
    """
    Simple in-memory cache.

    Production replacement:
    Redis / Memcached
    """

    def __init__(self):
        self.store = {}
        self.lock = asyncio.Lock()


    async def get(self, key: str) -> Optional[Any]:

        async with self.lock:

            item = self.store.get(key)

            if not item:
                return None


            if item.expired():
                del self.store[key]
                return None


            return item.value



    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300
    ):

        async with self.lock:

            self.store[key] = CacheItem(
                value,
                ttl
            )



    async def delete(self,key:str):

        async with self.lock:

            if key in self.store:
                del self.store[key]



    async def clear(self):

        async with self.lock:

            self.store.clear()



cache = MemoryCache()