
from __future__ import annotations

import inspect
import logging
from typing import Dict, Optional, Any

from .base import BaseConnector, ConnectorResult

logger = logging.getLogger(__name__)


class ConnectorManager:
    """
    Manages all data acquisition connectors.

    Example:
        SEC connector
        News connector
        Web connector
        Company database connector
    """

    def __init__(self):

        self.connectors: Dict[str, BaseConnector] = {}

        logger.info(
            "Connector manager initialized"
        )

    def register(
        self,
        connector: BaseConnector
    ):

        name = connector.name

        if name in self.connectors:
            raise ValueError(
                f"Connector already exists: {name}"
            )

        self.connectors[name] = connector

        logger.info(
            "Registered connector: %s",
            name
        )

    def unregister(
        self,
        name: str
    ):

        if name in self.connectors:
            del self.connectors[name]

    def get(
        self,
        name: str
    ) -> BaseConnector:

        connector = self.connectors.get(name)

        if not connector:
            raise KeyError(
                f"Connector not found: {name}"
            )

        return connector

    async def initialize(self) -> None:
        """
        Initialize all registered connectors.

        Connectors may optionally implement an async or
        synchronous initialize() method.
        """

        for name, connector in self.connectors.items():

            initialize = getattr(
                connector,
                "initialize",
                None
            )

            if initialize is None:
                logger.debug(
                    "Connector has no initialize method: %s",
                    name
                )
                continue

            result = initialize()

            if inspect.isawaitable(result):
                await result

            logger.info(
                "Initialized connector: %s",
                name
            )

    async def fetch(
        self,
        connector_name: str,
        query: Optional[str] = None,
        **kwargs
    ) -> ConnectorResult:

        connector = self.get(
            connector_name
        )

        return await connector.fetch(
            query=query,
            **kwargs
        )

    async def health_check(
        self
    ) -> Dict[str, Any]:

        results = {}

        for name, connector in self.connectors.items():

            results[name] = (
                await connector.health_check()
            )

        return results

    async def shutdown(self):

        for connector in self.connectors.values():

            await connector.close()

        logger.info(
            "All connectors closed"
        )

