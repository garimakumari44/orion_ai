"""
Retry utilities for transient execution failures.
"""

from __future__ import annotations

import functools
import time
from typing import Callable, Type


def retry(
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Type[Exception] | tuple[Type[Exception], ...] = Exception,
):
    """
    Retry decorator.

    Example:

        @retry(attempts=3)
        def execute():
            ...
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            current_delay = delay

            last_exception = None

            for attempt in range(1, attempts + 1):

                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    last_exception = exc

                    if attempt == attempts:
                        break

                    time.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator