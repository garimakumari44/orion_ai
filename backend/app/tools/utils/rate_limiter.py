import time
import asyncio
from collections import defaultdict



class RateLimiter:


    def __init__(
        self,
        max_requests:int = 10,
        window:int = 60
    ):

        self.max_requests = max_requests
        self.window = window

        self.requests = defaultdict(list)

        self.lock = asyncio.Lock()



    async def allow(
        self,
        key:str
    ):

        async with self.lock:

            now = time.time()


            history = self.requests[key]


            history[:] = [
                t for t in history
                if now - t < self.window
            ]


            if len(history) >= self.max_requests:

                return False


            history.append(now)

            return True




    async def wait(
        self,
        key:str
    ):

        while not await self.allow(key):

            await asyncio.sleep(1)



rate_limiter = RateLimiter(
    max_requests=20,
    window=60
)