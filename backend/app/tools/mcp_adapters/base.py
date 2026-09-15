"""
MCP Adapter Base

Defines the common interface for MCP adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class MCPAdapter(ABC):
    """
    Base class for MCP adapters.

    An adapter translates Orion's internal tool/capability
    interface into calls to an MCP server.
    """

    name: str = ""
    description: str = ""

    def __init__(self, client: Any) -> None:
        self.client = client

    @abstractmethod
    async def call(
        self,
        tool_name: str,
        arguments: Dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute an MCP tool.
        """
        raise NotImplementedError

    async def health_check(self) -> bool:
        """
        Check whether the underlying MCP connection is healthy.
        """
        try:
            await self.client.health_check()
            return True
        except Exception:
            return False