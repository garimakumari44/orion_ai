"""
Knowledge Index Manager.

Coordinates all indexing backends used by the Knowledge System.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .keyword_index import KeywordIndex

# Future imports
# from .vector_index import VectorIndex
# from .hybrid_index import HybridIndex


class IndexManager:
    """
    Central manager for all search indexes.

    Responsibilities
    ----------------
    - Initialize indexes
    - Build indexes
    - Refresh indexes
    - Shutdown indexes
    """

    def __init__(
        self,
        *,
        keyword_index: Optional[KeywordIndex] = None,
        # vector_index: Optional[VectorIndex] = None,
        # hybrid_index: Optional[HybridIndex] = None,
    ) -> None:

        self.keyword_index = keyword_index or KeywordIndex()

        # Future
        self.vector_index = None
        self.hybrid_index = None

        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """
        Initialize indexing subsystem.
        """

        if self._initialized:
            return

        if hasattr(self.keyword_index, "initialize"):
            await self.keyword_index.initialize()

        self._initialized = True

    async def shutdown(self) -> None:
        """
        Shutdown indexing subsystem.
        """

        if not self._initialized:
            return

        if hasattr(self.keyword_index, "close"):
            result = self.keyword_index.close()

            if hasattr(result, "__await__"):
                await result

        self._initialized = False

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    async def index(
        self,
        documents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Build every configured index.
        """

        if hasattr(self.keyword_index, "build"):
            await self.keyword_index.build(documents)

        return documents

    async def rebuild(
        self,
        documents: List[Dict[str, Any]],
    ) -> None:
        """
        Rebuild all indexes from scratch.
        """

        await self.index(documents)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health(self) -> Dict[str, Any]:
        """
        Health information.
        """

        return {
            "initialized": self._initialized,
            "keyword_index": self.keyword_index is not None,
            "vector_index": self.vector_index is not None,
            "hybrid_index": self.hybrid_index is not None,
        }