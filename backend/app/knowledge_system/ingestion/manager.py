
"""
Knowledge Ingestion Manager.

Coordinates document ingestion from external connectors into the
knowledge processing pipeline.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class IngestionManager:
    """
    Orchestrates ingestion of raw documents.

    Responsibilities
    ----------------
    - Receive raw documents
    - Validate inputs
    - Dispatch ingestion pipeline
    - Maintain ingestion state
    """

    def __init__(self) -> None:
        self._documents: List[Dict[str, Any]] = []
        self._initialized: bool = False

    async def initialize(self) -> None:
        """
        Initialize the ingestion subsystem.

        The current ingestion manager does not require any external
        resources, workers, or connections, but it participates in the
        common Knowledge System lifecycle.
        """

        if self._initialized:
            logger.debug(
                "Ingestion manager already initialized"
            )
            return

        self._initialized = True

        logger.info(
            "Ingestion manager initialized"
        )

    def ingest(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ingest raw documents.

        Parameters
        ----------
        documents : List[Dict]

        Returns
        -------
        List[Dict]
        """

        self._documents.extend(documents)

        logger.debug(
            "Ingested %d documents",
            len(documents)
        )

        return documents

    def count(self) -> int:
        """Return total ingested documents."""

        return len(self._documents)

    def clear(self) -> None:
        """Clear ingestion cache."""

        self._documents.clear()

        logger.debug(
            "Ingestion documents cleared"
        )

