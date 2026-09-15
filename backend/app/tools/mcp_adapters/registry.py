"""
MCP Adapter Registry

Central registry for MCP adapters.
"""

from __future__ import annotations

from typing import Dict

from .base import MCPAdapter


class MCPAdapterRegistry:
    """
    Registry of MCP adapters available to Orion.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, MCPAdapter] = {}

    def register(self, adapter: MCPAdapter) -> None:
        """
        Register an MCP adapter.
        """

        if not adapter.name:
            raise ValueError(
                "MCP adapter must define a name."
            )

        if adapter.name in self._adapters:
            raise ValueError(
                f"MCP adapter already registered: {adapter.name}"
            )

        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> MCPAdapter:
        """
        Retrieve an adapter by name.
        """

        try:
            return self._adapters[name]
        except KeyError:
            raise KeyError(
                f"MCP adapter not found: {name}"
            ) from None

    def unregister(self, name: str) -> None:
        """
        Remove an adapter.
        """
        self._adapters.pop(name, None)

    def list(self) -> list[str]:
        """
        Return registered adapter names.
        """
        return list(self._adapters.keys())

    def clear(self) -> None:
        """
        Remove all registered adapters.
        """
        self._adapters.clear()