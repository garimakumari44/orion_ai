"""
tool_calls.py

Responsible for executing tools.

The execution engine is intentionally lightweight.
Future versions will support:

- retries
- async execution
- parallel tools
- timeout handling
- permission checks
"""

from __future__ import annotations

import inspect
import logging
from typing import Any, Callable, Dict

from .schema import ToolCall, ToolResult

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes registered tools.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Any]] = {}

    # -----------------------------------------------------

    def register(
        self,
        name: str,
        function: Callable[..., Any],
    ) -> None:
        """
        Register a callable.
        """

        if name in self._tools:
            raise ValueError(f"Tool '{name}' already exists.")

        self._tools[name] = function

        logger.info("Registered tool: %s", name)

    # -----------------------------------------------------

    def unregister(self, name: str) -> None:
        """
        Remove a tool.
        """

        self._tools.pop(name, None)

    # -----------------------------------------------------

    def list_tools(self):
        return list(self._tools.keys())

    # -----------------------------------------------------

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    # -----------------------------------------------------

    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """
        Execute a tool request.
        """

        if call.tool_name not in self._tools:
            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error="Unknown tool.",
            )

        fn = self._tools[call.tool_name]

        try:

            if inspect.iscoroutinefunction(fn):
                result = await fn(**call.arguments)

            else:
                result = fn(**call.arguments)

            return ToolResult(
                tool_name=call.tool_name,
                success=True,
                output=result,
            )

        except Exception as exc:

            logger.exception(exc)

            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error=str(exc),
            )


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

tool_executor = ToolExecutor()