"""
Retry utilities.

Features
--------
- Exponential backoff
- Optional jitter
- Exception filtering
- Configurable retries
- Sync function support
"""

from __future__ import annotations

import random
import time
from functools import wraps
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def retry(
    *,
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float | None = 60.0,
    jitter: bool = True,
    exceptions: Iterable[type[Exception]] = (Exception,),
):
    """
    Retry decorator.

    Example
    -------
    @retry(retries=5)
    def fetch():
        ...
    """

    exceptions = tuple(exceptions)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:

            current_delay = delay

            for attempt in range(retries + 1):

                try:
                    return func(*args, **kwargs)

                except exceptions:

                    if attempt == retries:
                        raise

                    sleep = current_delay

                    if jitter:
                        sleep *= random.uniform(0.8, 1.2)

                    time.sleep(sleep)

                    current_delay *= backoff

                    if max_delay is not None:
                        current_delay = min(current_delay, max_delay)

        return wrapper

    return decorator