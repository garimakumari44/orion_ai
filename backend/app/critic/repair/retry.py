"""
retry.py

Retry execution utilities.

Used by:
- Execution Engine
- Tool Router
- LLM calls
- Research pipeline
"""

import time
import random

from dataclasses import dataclass
from typing import Callable, Any, Optional



@dataclass
class RetryPolicy:
    """
    Defines retry behaviour.
    """

    max_retries: int = 3

    initial_delay: float = 1.0

    max_delay: float = 20.0

    backoff_factor: float = 2.0

    enable_jitter: bool = True



@dataclass
class RetryResponse:
    """
    Result after retry execution.
    """

    success: bool

    value: Any = None

    attempts: int = 0

    error: Optional[str] = None



class RetryExecutor:
    """
    Executes operations with retry support.
    """


    def __init__(
        self,
        policy: RetryPolicy | None = None
    ):

        self.policy = (
            policy
            or RetryPolicy()
        )



    def run(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> RetryResponse:


        last_error = None


        for attempt in range(
            1,
            self.policy.max_retries + 1
        ):

            try:

                result = operation(
                    *args,
                    **kwargs
                )


                return RetryResponse(
                    success=True,
                    value=result,
                    attempts=attempt
                )


            except Exception as error:

                last_error = str(error)


                if attempt < self.policy.max_retries:

                    delay = self._get_delay(
                        attempt
                    )

                    time.sleep(delay)



        return RetryResponse(
            success=False,
            attempts=self.policy.max_retries,
            error=last_error
        )



    def _get_delay(
        self,
        attempt: int
    ):


        delay = (
            self.policy.initial_delay
            *
            (
                self.policy.backoff_factor
                **
                (attempt - 1)
            )
        )


        delay = min(
            delay,
            self.policy.max_delay
        )


        if self.policy.enable_jitter:

            delay += random.random()


        return delay