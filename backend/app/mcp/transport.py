from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class TransportError(Exception):
    """
    Raised when transport communication fails.
    """
    pass


class BaseTransport(ABC):
    """
    Abstract communication layer.

    Every MCP transport must implement:
    - send request
    - receive response
    """

    @abstractmethod
    async def send(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def close(self):
        pass



class HTTPTransport(BaseTransport):
    """
    HTTP based MCP transport.

    Used when MCP server is running remotely.

    Example:

    Orion AI
        |
        HTTPTransport
        |
    MCP Server
    """

    def __init__(
        self,
        endpoint: str,
        timeout: int = 30
    ):
        self.endpoint = endpoint
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            timeout=timeout
        )


    async def send(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        try:

            response = await self.client.post(
                self.endpoint,
                json=payload
            )

            response.raise_for_status()

            return response.json()


        except Exception as e:

            logger.error(
                "HTTP transport failed",
                exc_info=True
            )

            raise TransportError(
                str(e)
            )



    async def close(self):

        await self.client.aclose()



class StdioTransport(BaseTransport):
    """
    Local process MCP transport.

    Example:

    Orion AI
        |
        stdin/stdout
        |
    Local MCP Server Process

    Common for:
    - filesystem tools
    - local code execution
    - developer tools
    """

    def __init__(self, process):
        self.process = process


    async def send(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        try:

            message = json.dumps(payload)

            self.process.stdin.write(
                message.encode()
            )

            await self.process.stdin.drain()


            response = await self.process.stdout.readline()


            return json.loads(
                response.decode()
            )


        except Exception as e:

            logger.error(
                "stdio transport failed",
                exc_info=True
            )

            raise TransportError(
                str(e)
            )



    async def close(self):

        if self.process:

            self.process.terminate()
