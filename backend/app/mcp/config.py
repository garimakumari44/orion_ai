from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(slots=True)
class MCPConfig:
    """
    Configuration for an MCP client connection.

    This object centralizes all runtime configuration used by the
    transport, session, and client layers.
    """

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    server_url: str
    timeout: float = 30.0
    connect_timeout: float = 10.0

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    max_retries: int = 3
    retry_delay: float = 1.0

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    api_key: Optional[str] = None
    bearer_token: Optional[str] = None

    # ------------------------------------------------------------------
    # TLS / SSL
    # ------------------------------------------------------------------

    verify_ssl: bool = True

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    headers: Dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Connection Pool
    # ------------------------------------------------------------------

    max_connections: int = 20
    keep_alive: bool = True

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    debug: bool = False

    # ------------------------------------------------------------------

    def merged_headers(self) -> Dict[str, str]:
        """
        Build request headers including authentication.
        """

        headers = dict(self.headers)

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        return headers

    def copy_with(self, **updates) -> "MCPConfig":
        """
        Return a copy of this configuration with selected fields updated.
        """

        data = self.__dict__.copy()
        data.update(updates)
        return MCPConfig(**data)