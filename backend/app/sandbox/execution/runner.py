"""
Execution orchestrator.

Coordinates:
- Kernel execution
- Timing
- Error handling
- Result creation
"""

from __future__ import annotations

import time
import traceback
from datetime import datetime
from typing import Any

from sandbox.execution.result import (
    ExecutionMetrics,
    ExecutionResult,
)


class ExecutionRunner:
    """
    Executes code using a kernel.

    Any kernel only needs:

        kernel.execute(code)

    returning:

        result
    """

    def run(
        self,
        kernel: Any,
        code: str,
        **kwargs,
    ) -> ExecutionResult:
        """
        Execute code using a kernel.
        """

        started = datetime.utcnow()
        start = time.perf_counter()

        try:
            output = kernel.execute(code, **kwargs)

            elapsed = time.perf_counter() - start

            return ExecutionResult(
                success=True,
                result=output,
                metrics=ExecutionMetrics(
                    execution_time=elapsed,
                ),
                started_at=started,
                finished_at=datetime.utcnow(),
            )

        except Exception as exc:

            elapsed = time.perf_counter() - start

            return ExecutionResult(
                success=False,
                exception=str(exc),
                traceback=traceback.format_exc(),
                metrics=ExecutionMetrics(
                    execution_time=elapsed,
                ),
                started_at=started,
                finished_at=datetime.utcnow(),
            )

    async def arun(
        self,
        kernel: Any,
        code: str,
        **kwargs,
    ) -> ExecutionResult:
        """
        Async execution.
        """

        started = datetime.utcnow()
        start = time.perf_counter()

        try:
            output = await kernel.execute(code, **kwargs)

            elapsed = time.perf_counter() - start

            return ExecutionResult(
                success=True,
                result=output,
                metrics=ExecutionMetrics(
                    execution_time=elapsed,
                ),
                started_at=started,
                finished_at=datetime.utcnow(),
            )

        except Exception as exc:

            elapsed = time.perf_counter() - start

            return ExecutionResult(
                success=False,
                exception=str(exc),
                traceback=traceback.format_exc(),
                metrics=ExecutionMetrics(
                    execution_time=elapsed,
                ),
                started_at=started,
                finished_at=datetime.utcnow(),
            )