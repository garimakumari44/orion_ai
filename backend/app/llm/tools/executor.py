"""
executor.py

High-level orchestration layer for tool execution.

Supports:
- Local Python tools
- MCP remote tools
- Validation
- Metrics
- Error handling
"""

from __future__ import annotations


import inspect
import logging
import time
from typing import Any, Callable, Dict, Optional


from .schema import ToolCall, ToolResult
from .validator import ToolValidator, ValidationError


# MCP Integration
from app.tools.mcp.mcp_tool_executor import MCPToolExecutor


logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Unified production tool executor.

    Execution sources:
        1. Local tools
        2. MCP tools
    """

    def __init__(
        self,
        mcp_executor: Optional[MCPToolExecutor] = None,
    ) -> None:


        # Local python tools
        self._registry: Dict[str, Callable[..., Any]] = {}


        # MCP executor
        self._mcp_executor = mcp_executor


    # ==================================================
    # LOCAL TOOL MANAGEMENT
    # ==================================================


    def register(
        self,
        name: str,
        function: Callable[..., Any],
    ) -> None:
        """
        Register local python tool.
        """

        if name in self._registry:
            raise ValueError(
                f"Tool '{name}' already exists."
            )


        self._registry[name] = function



    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove local tool.
        """

        self._registry.pop(
            name,
            None
        )



    def list_tools(self) -> list[str]:
        """
        Return available local tools.
        """

        return sorted(
            self._registry.keys()
        )



    # ==================================================
    # MCP MANAGEMENT
    # ==================================================


    def attach_mcp_executor(
        self,
        executor: MCPToolExecutor,
    ):
        """
        Attach MCP tool runtime.
        """

        self._mcp_executor = executor



    async def list_all_tools(self):

        """
        Return both local and MCP tools.
        """

        tools = {
            "local": self.list_tools(),
            "mcp": []
        }


        if self._mcp_executor:

            tools["mcp"] = (
                await self._mcp_executor.list_tools()
            )


        return tools



    # ==================================================
    # EXECUTION
    # ==================================================


    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """
        Execute either local or MCP tool.
        """


        start = time.perf_counter()


        try:


            #
            # 1. Check local tools
            #
            if call.tool_name in self._registry:


                function = ToolValidator.validate(
                    call,
                    self._registry,
                )


                if inspect.iscoroutinefunction(function):

                    output = await function(
                        **call.arguments
                    )

                else:

                    output = function(
                        **call.arguments
                    )


            #
            # 2. Check MCP tools
            #
            elif self._mcp_executor:


                logger.info(
                    "Executing MCP tool: %s",
                    call.tool_name,
                )


                output = await self._mcp_executor.execute(
                    tool_name=call.tool_name,
                    arguments=call.arguments,
                )


            #
            # 3. Tool not found
            #
            else:

                raise ValueError(
                    f"Tool '{call.tool_name}' not found."
                )



            elapsed = (
                time.perf_counter()
                -
                start
            )


            logger.info(
                "Tool %s completed in %.3fs",
                call.tool_name,
                elapsed,
            )


            return ToolResult(

                tool_name=call.tool_name,

                success=True,

                output=output,

            )



        except ValidationError as exc:


            logger.warning(
                "Validation failed: %s",
                exc,
            )


            return ToolResult(

                tool_name=call.tool_name,

                success=False,

                error=str(exc),

            )



        except Exception as exc:


            logger.exception(
                "Tool execution failed"
            )


            return ToolResult(

                tool_name=call.tool_name,

                success=False,

                error=str(exc),

            )



# ======================================================
# GLOBAL INSTANCE
# ======================================================


executor = ToolExecutor()