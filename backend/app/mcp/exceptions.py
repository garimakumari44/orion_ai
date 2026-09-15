# mcp/exceptions.py

from __future__ import annotations


class MCPError(Exception):
    """
    Base exception for all MCP related errors.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
    ):
        self.message = message
        self.code = code

        super().__init__(message)

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"

        return self.message


class MCPConnectionError(MCPError):
    """
    Raised when MCP client cannot connect to a server.
    """

    def __init__(
        self,
        message: str = "Failed to connect to MCP server",
    ):
        super().__init__(
            message,
            code="CONNECTION_ERROR",
        )


class MCPTimeoutError(MCPError):
    """
    Raised when MCP request exceeds timeout.
    """

    def __init__(
        self,
        message: str = "MCP request timed out",
    ):
        super().__init__(
            message,
            code="TIMEOUT",
        )


class MCPProtocolError(MCPError):
    """
    Raised when MCP messages violate protocol rules.
    """

    def __init__(
        self,
        message: str = "Invalid MCP protocol message",
    ):
        super().__init__(
            message,
            code="PROTOCOL_ERROR",
        )


class MCPDiscoveryError(MCPError):
    """
    Raised when discovering MCP capabilities fails.
    """

    def __init__(
        self,
        message: str = "MCP capability discovery failed",
    ):
        super().__init__(
            message,
            code="DISCOVERY_ERROR",
        )


class MCPRegistryError(MCPError):
    """
    Raised when tool/resource registration fails.
    """

    def __init__(
        self,
        message: str = "MCP registry operation failed",
    ):
        super().__init__(
            message,
            code="REGISTRY_ERROR",
        )


class MCPToolExecutionError(MCPError):
    """
    Raised when an MCP tool execution fails.
    """

    def __init__(
        self,
        message: str = "MCP tool execution failed",
    ):
        super().__init__(
            message,
            code="TOOL_EXECUTION_ERROR",
        )


class MCPAuthenticationError(MCPError):
    """
    Raised when authentication with MCP provider fails.
    """

    def __init__(
        self,
        message: str = "MCP authentication failed",
    ):
        super().__init__(
            message,
            code="AUTH_ERROR",
        )


class MCPInvalidRequestError(MCPError):
    """
    Raised when an MCP request is malformed.
    """

    def __init__(
        self,
        message: str = "Invalid MCP request",
    ):
        super().__init__(
            message,
            code="INVALID_REQUEST",
        )
        
class MCPSessionError(MCPError):
    """
    Raised when MCP session state is invalid.

    Examples:
    - sending request before connection
    - initializing before connection
    - using closed session
    - invalid session lifecycle operation
    """

    def __init__(
        self,
        message: str = "Invalid MCP session state",
    ):
        super().__init__(
            message,
            code="SESSION_ERROR",
        )