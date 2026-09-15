"""
retry_manager.py

Centralized retry logic for tool execution.

Responsibilities
----------------
- Retry transient failures
- Retry failed tool execution results
- Exponential backoff
- Configurable retry policy
- Return structured retry metadata
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


# ============================================================
# Retry Result
# ============================================================

@dataclass(slots=True)
class RetryResult:
    """
    Result returned after retry execution.
    """

    success: bool
    output: Any | None
    error: str | None
    attempts: int


# ============================================================
# Retry Manager
# ============================================================

class RetryManager:
    """
    Handles retrying async operations using exponential backoff.

    Supports two failure styles:

    1. Exception based failure

       Example:
           raise Exception("API unavailable")


    2. Result based failure

       Example:
           ToolExecutionResult(
               success=False,
               error="Tool failed"
           )

    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
    ) -> None:

        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor


    async def run(
        self,
        operation: Callable[..., Awaitable[Any]],
        *args: Any,
        retry_exceptions: tuple[type[Exception], ...] = (Exception,),
        **kwargs: Any,
    ) -> RetryResult:
        """
        Execute an async operation with retries.

        Returns
        -------
        RetryResult

        Behaviour:

        success:
            returns immediately

        failure:
            retries until max_retries exhausted

        """

        delay = self.initial_delay
        attempts = 0


        while True:

            attempts += 1


            try:

                result = await operation(
                    *args,
                    **kwargs,
                )


                # ==================================================
                # Handle returned failure objects
                #
                # Example:
                # ToolExecutionResult(success=False)
                # ==================================================

                if hasattr(result, "success"):

                    if result.success is False:


                        # Retries exhausted
                        if attempts > self.max_retries:

                            return RetryResult(
                                success=False,
                                output=result,
                                error=getattr(
                                    result,
                                    "error",
                                    "Operation failed",
                                ),
                                attempts=attempts,
                            )


                        # Retry after delay
                        await asyncio.sleep(delay)

                        delay *= self.backoff_factor

                        continue



                # ==================================================
                # Successful execution
                # ==================================================

                return RetryResult(
                    success=True,
                    output=result,
                    error=None,
                    attempts=attempts,
                )



            # ======================================================
            # Handle exception failures
            # ======================================================

            except retry_exceptions as exc:


                if attempts > self.max_retries:

                    return RetryResult(
                        success=False,
                        output=None,
                        error=str(exc),
                        attempts=attempts,
                    )


                await asyncio.sleep(delay)

                delay *= self.backoff_factor