from __future__ import annotations

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from .transport  import  BaseTransport
from .protocol import MCPRequest, MCPResponse
from .exceptions import (

    MCPConnectionError
)
from .exceptions  import MCPSessionError



logger = logging.getLogger(__name__)


class MCPSession:
    """
    Represents an active MCP communication session.

    A session manages:
    - connection lifecycle
    - request/response communication
    - server capabilities
    - session metadata
    """

    def __init__(
        self,
        transport: BaseTransport,
    ):
        self.session_id = str(uuid.uuid4())

        self.transport = transport

        self.created_at = datetime.utcnow()

        self.connected = False
        self.initialized = False

        self.server_info: Dict[str, Any] = {}

        self.pending_requests: Dict[str, MCPRequest] = {}


    async def connect(self):
        """
        Establish connection with MCP server.
        """

        if self.connected:
            return

        try:
            await self.transport.connect()

            self.connected = True

            logger.info(
                "MCP session connected",
                extra={
                    "session_id": self.session_id
                }
            )

        except Exception as exc:
            raise ConnectionError(
                f"Failed to connect MCP session: {exc}"
            )


    async def initialize(self):
        """
        Perform MCP initialization handshake.

        Client tells server:
        - protocol version
        - client capabilities

        Server returns:
        - server capabilities
        - supported tools/resources
        """

        if not self.connected:
            raise MCPSessionError(
                "Session is not connected"
            )


        request = MCPRequest(
            method="initialize",
            params={
                "protocol_version": "1.0",
                "client": {
                    "name": "Orion-MCP-Client",
                    "version": "0.1.0"
                }
            }
        )


        response = await self.send(request)


        self.server_info = response.result

        self.initialized = True


        logger.info(
            "MCP session initialized",
            extra={
                "server": self.server_info
            }
        )


    async def send(
        self,
        request: MCPRequest
    ) -> MCPResponse:
        """
        Send request through transport
        and wait for response.
        """

        if not self.connected:
            raise MCPSessionError(
                "Cannot send request. Session disconnected."
            )


        request_id = request.id


        self.pending_requests[request_id] = request


        try:

            response = await self.transport.send(
                request
            )

            return response


        finally:

            self.pending_requests.pop(
                request_id,
                None
            )


    async def close(self):
        """
        Close MCP session.
        """

        if not self.connected:
            return


        await self.transport.close()


        self.connected = False
        self.initialized = False


        logger.info(
            "MCP session closed",
            extra={
                "session_id": self.session_id
            }
        )


    def get_server_capabilities(self):
        """
        Return capabilities exposed by MCP server.
        """

        return self.server_info.get(
            "capabilities",
            {}
        )


    def is_ready(self) -> bool:
        """
        Check whether session can execute MCP requests.
        """

        return (
            self.connected
            and self.initialized
        )