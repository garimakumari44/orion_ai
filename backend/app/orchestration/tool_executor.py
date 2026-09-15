"""
Tool Executor

Responsible for safely executing tools selected by the orchestration layer.

Responsibilities
----------------
- Execute a tool
- Measure execution time
- Handle failures
- Retry transient errors
- Return standardized results
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.tools.base_tool import BaseTool
from app.schemas import ToolExecutionResult

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes a tool instance.

    The executor never decides WHICH tool to use.
    It only executes the tool it receives.
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 2,
    ):
        self.timeout = timeout
        self.max_retries = max_retries

    async def execute(
        self,
        tool: BaseTool,
        **kwargs: Any,
    ) -> ToolExecutionResult:
        """
        Execute a tool safely.

        Parameters
        ----------
        tool
            Tool instance

        kwargs
            Input arguments passed to the tool

        Returns
        -------
        ToolExecutionResult
        """

        start = time.perf_counter()

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:
                logger.info(
                    "Executing tool '%s' (attempt %s)",
                    tool.name,
                    attempt + 1,
                )

                result = await tool.execute(**kwargs)

                duration = time.perf_counter() - start

                return ToolExecutionResult(
                    tool_name=tool.name,
                    success=True,
                    data=result,
                    latency=duration,
                    error=None,
                )

            except Exception as exc:

                logger.exception(
                    "Tool '%s' failed",
                    tool.name,
                )

                last_error = str(exc)

        duration = time.perf_counter() - start

        return ToolExecutionResult(
            tool_name=tool.name,
            success=False,
            data=None,
            latency=duration,
            error=last_error,
        )