"""
Execution timeout utilities.
"""

from __future__ import annotations

import functools
import signal


class TimeoutError(RuntimeError):
    """Raised when execution exceeds the time limit."""


class Timeout:
    """
    Unix signal-based timeout.

    Example:
        with Timeout(5):
            run_code()
    """

    def __init__(self, seconds: int):
        self.seconds = seconds

    def _handler(self, signum, frame):
        raise TimeoutError(
            f"Execution exceeded {self.seconds} seconds."
        )

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        signal.alarm(0)


def timeout(seconds: int):
    """
    Decorator for limiting execution time.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with Timeout(seconds):
                return func(*args, **kwargs)

        return wrapper

    return decorator