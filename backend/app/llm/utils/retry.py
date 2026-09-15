"""
Generic retry utilities.

Supports:
- Exponential backoff
- Configurable exceptions
- Jitter
- Sync + Async functions
"""

from __future__ import annotations

import asyncio
import random
import time
from functools import wraps
from typing import Any, Callable, Iterable, Tuple, Type


def retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float | None = None,
    jitter: bool = True,
):
    """
    Retry decorator.

    Example:
        @retry((TimeoutError,), attempts=5)
        def call():
            ...

    """

    def decorator(func: Callable):

        @wraps(func)
        def wrapper(*args, **kwargs):

            current_delay = delay
            last_exception = None

            for attempt in range(1, attempts + 1):

                try:
                    return func(*args, **kwargs)

                except exceptions as exc:

                    last_exception = exc

                    if attempt == attempts:
                        raise

                    sleep = current_delay

                    if jitter:
                        sleep *= random.uniform(0.8, 1.2)

                    if max_delay:
                        sleep = min(sleep, max_delay)

                    time.sleep(sleep)

                    current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator


def async_retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float | None = None,
    jitter: bool = True,
):
    """
    Retry decorator for async functions.
    """

    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            current_delay = delay
            last_exception = None

            for attempt in range(1, attempts + 1):

                try:
                    return await func(*args, **kwargs)

                except exceptions as exc:

                    last_exception = exc

                    if attempt == attempts:
                        raise

                    sleep = current_delay

                    if jitter:
                        sleep *= random.uniform(0.8, 1.2)

                    if max_delay:
                        sleep = min(sleep, max_delay)

                    await asyncio.sleep(sleep)

                    current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator