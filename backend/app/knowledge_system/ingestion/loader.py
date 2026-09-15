"""
Loads raw content from connectors.

This module is intentionally simple.
It only retrieves data and wraps it into a common structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RawDocument:
    """
    Raw document returned from a connector.

    Content may be:
        - bytes
        - str
        - JSON dict
        - API response
    """

    id: str
    source: str
    content: Any
    metadata: dict


class DocumentLoader:
    """
    Standard loader used by the ingestion pipeline.
    """

    async def load(self, connector, item) -> RawDocument:
        """
        Load one document from a connector.

        Parameters
        ----------
        connector:
            Connector implementing read()

        item:
            Connector-specific identifier.

        Returns
        -------
        RawDocument
        """

        result = await connector.read(item)

        return RawDocument(
            id=result.id,
            source=result.source,
            content=result.content,
            metadata=result.metadata,
        )