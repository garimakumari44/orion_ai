"""
Document deduplication.

Removes exact and near-duplicate chunks before reranking.
"""

from __future__ import annotations

from typing import List

from app.knowledge_system.models.chunk  import Chunk


class Deduplicator:
    """
    Deduplicate retrieved chunks.

    Strategies:
    - chunk id
    - document id
    - text hash
    """

    def deduplicate(
        self,
        documents: List[Chunk],
    ) -> List[Chunk]:

        seen = set()
        unique = []

        for doc in documents:

            key = getattr(
                doc,
                "hash",
                None,
            )

            if key is None:
                key = (
                    str(doc.document_id),
                    doc.text.strip(),
                )

            if key in seen:
                continue

            seen.add(key)
            unique.append(doc)

        return unique

    def deduplicate_by_document(
        self,
        documents: List[Chunk],
    ) -> List[Chunk]:

        best = {}

        for doc in documents:

            doc_id = str(doc.document_id)

            if (
                doc_id not in best
                or doc.score > best[doc_id].score
            ):
                best[doc_id] = doc

        return sorted(
            best.values(),
            key=lambda d: d.score,
            reverse=True,
        )