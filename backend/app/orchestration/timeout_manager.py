"""
timeout_manager.py

Centralized timeout handling for tool execution.

Responsibilities
----------------
- Apply execution timeout
- Cancel long-running tasks
- Produce consistent timeout results
- Measure execution duration
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class TimeoutResult:
    """
    Result returned after timeout handling.
    """

    success: bool
    output: Any | None
    error: str | None
    execution_time: float
    timed_out: bool


# ============================================================
# Timeout Manager
# ============================================================

class TimeoutManager:
    """
    Executes async operations with timeout protection.
    """

    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout

    async def run(
        self,
        operation: Callable[..., Awaitable[Any]],
        *args,
        timeout: float | None = None,
        **kwargs,
    ) -> TimeoutResult:
        """
        Execute an async operation with timeout.

        Parameters
        ----------
        operation:
            Async callable.

        timeout:
            Optional timeout override.
        """

        timeout = timeout or self.default_timeout

        start = time.perf_counter()

        try:

            result = await asyncio.wait_for(
                operation(*args, **kwargs),
                timeout=timeout,
            )

            elapsed = time.perf_counter() - start

            return TimeoutResult(
                success=True,
                output=result,
                error=None,
                execution_time=elapsed,
                timed_out=False,
            )

        except asyncio.TimeoutError:

            elapsed = time.perf_counter() - start

            return TimeoutResult(
                success=False,
                output=None,
                error=f"Execution exceeded timeout ({timeout}s)",
                execution_time=elapsed,
                timed_out=True,
            )

        except Exception as exc:

            elapsed = time.perf_counter() - start

            return TimeoutResult(
                success=False,
                output=None,
                error=str(exc),
                execution_time=elapsed,
                timed_out=False,
            )