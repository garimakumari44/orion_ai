"""
MCP (Model Context Protocol) package.

This package provides the infrastructure for communicating with external
Model Context Protocol (MCP) servers. It handles server discovery,
session management, protocol communication, and exposes a high-level
client used by the orchestration layer.

Typical usage:

    from app.mcp import MCPClient

    client = MCPClient(...)
"""

from .client import MCPClient

__all__ = [
    "MCPClient",
]