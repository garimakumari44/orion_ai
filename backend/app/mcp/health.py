from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class MCPHealthStatus:
    """
    Health information for an MCP server.
    """

    server_name: str

    healthy: bool = False

    latency_ms: float = 0.0

    last_checked: Optional[datetime] = None

    failures: int = 0

    metadata: Dict[str, str] = field(default_factory=dict)


class MCPHealthMonitor:
    """
    Monitors MCP server health.

    Responsibilities:
    - Ping MCP servers
    - Measure latency
    - Track failures
    - Provide health reports
    """

    def __init__(self):
        self._servers: Dict[str, MCPHealthStatus] = {}


    def register_server(
        self,
        server_name: str
    ):
        """
        Register a new MCP server.
        """

        if server_name not in self._servers:

            self._servers[server_name] = MCPHealthStatus(
                server_name=server_name
            )


    async def check_health(
        self,
        server_name: str,
        ping_function
    ) -> MCPHealthStatus:
        """
        Check MCP server health.

        ping_function:
            async callable that verifies server availability
        """

        self.register_server(server_name)

        status = self._servers[server_name]

        start = time.perf_counter()

        try:

            await ping_function()

            latency = (
                time.perf_counter() - start
            ) * 1000


            status.healthy = True
            status.latency_ms = latency
            status.failures = 0
            status.last_checked = datetime.utcnow()


        except Exception as exc:

            status.healthy = False
            status.failures += 1
            status.last_checked = datetime.utcnow()

            status.metadata["error"] = str(exc)


        return status



    def get_status(
        self,
        server_name: str
    ) -> Optional[MCPHealthStatus]:

        return self._servers.get(server_name)



    def get_all_status(
        self
    ) -> Dict[str, MCPHealthStatus]:

        return self._servers