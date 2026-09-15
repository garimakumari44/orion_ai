"""
adaptive_retrieval/ranking/result_merger.py

Merge retrieval results coming from multiple retrieval sources.

Responsibilities
----------------
- Remove duplicate documents
- Merge metadata
- Preserve provenance
- Combine retrieval scores
"""

from __future__ import annotations

import hashlib
from typing import Dict, List

from app.knowledge_system.types import RetrievedDocument


class ResultMerger:
    """
    Merge duplicate retrieval results into a single document.
    """

    def __init__(self) -> None:
        pass

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def merge(
        self,
        documents: List[RetrievedDocument],
    ) -> List[RetrievedDocument]:
        """
        Merge duplicate retrieval results.

        Duplicate detection priority

        1. metadata["id"]
        2. document.id
        3. hash(document)
        """

        merged: Dict[str, RetrievedDocument] = {}

        for doc in documents:

            key = self._document_key(doc)

            if key not in merged:

                metadata = dict(doc.metadata)

                metadata.setdefault(
                    "sources",
                    [doc.source] if doc.source else [],
                )

                merged[key] = RetrievedDocument(
                    document=doc.document,
                    score=doc.score,
                    source=doc.source,
                    metadata=metadata,
                )

                continue

            existing = merged[key]

            # Keep highest retrieval score
            existing.score = max(
                existing.score,
                doc.score,
            )

            # Merge metadata
            existing.metadata.update(doc.metadata)

            # Merge provenance
            sources = set(
                existing.metadata.get(
                    "sources",
                    [],
                )
            )

            if doc.source:
                sources.add(doc.source)

            existing.metadata["sources"] = sorted(
                sources
            )

        return sorted(
            merged.values(),
            key=lambda d: d.score,
            reverse=True,
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _document_key(
        self,
        doc: RetrievedDocument,
    ) -> str:
        """
        Produce a stable key for duplicate detection.
        """

        if "id" in doc.metadata:
            return str(doc.metadata["id"])

        if hasattr(doc.document, "id"):
            return str(doc.document.id)

        return hashlib.sha256(
            repr(doc.document).encode("utf-8")
        ).hexdigest()

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    async def health(self):
        return {
            "status": "healthy",
            "component": "result_merger",
        }

    async def close(self):
        return None