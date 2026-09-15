from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class ConnectorResult:
    """
    Standard output format from all connectors.
    """

    def __init__(
        self,
        source: str,
        data: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.source = source
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseConnector(ABC):
    """
    Abstract connector interface.

    Every data source connector must implement this.
    """

    name: str = "base"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.config = config or {}

        logger.info(
            "Initialized connector: %s",
            self.name
        )


    @abstractmethod
    async def connect(self) -> bool:
        """
        Initialize connection.
        """
        pass


    @abstractmethod
    async def fetch(
        self,
        query: Optional[str] = None,
        **kwargs
    ) -> ConnectorResult:
        """
        Fetch raw data.
        """
        pass


    async def health_check(self) -> Dict[str, Any]:

        try:
            status = await self.connect()

            return {
                "connector": self.name,
                "status": "healthy" if status else "failed"
            }

        except Exception as e:

            return {
                "connector": self.name,
                "status": "error",
                "error": str(e)
            }


    async def close(self):
        """
        Optional cleanup.
        """

        logger.info(
            "Closing connector %s",
            self.name
        )