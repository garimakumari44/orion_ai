"""
Temporal Retriever

Ranks documents according to timestamps.

Useful for:
- Latest news
- Recent documentation
- Versioned knowledge
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from app.knowledge_system.models.chunk import Chunk




class TemporalRetriever:

    def __init__(self):
        pass

    def retrieve_latest(
        self,
        chunks: List[Chunk],
        limit: int = 10,
    ) -> List[Chunk]:

        def timestamp(chunk):

            ts = chunk.metadata.get("timestamp")

            if isinstance(ts, datetime):
                return ts

            return datetime.min

        return sorted(
            chunks,
            key=timestamp,
            reverse=True,
        )[:limit]

    def retrieve_between(
        self,
        chunks: List[Chunk],
        start: datetime,
        end: datetime,
    ) -> List[Chunk]:

        results = []

        for chunk in chunks:

            ts = chunk.metadata.get("timestamp")

            if not isinstance(ts, datetime):
                continue

            if start <= ts <= end:
                results.append(chunk)

        return results

    def score_recency(
        self,
        chunks: List[Chunk],
    ) -> List[tuple[Chunk, float]]:

        now = datetime.utcnow()

        scored = []

        for chunk in chunks:

            ts = chunk.metadata.get("timestamp")

            if not isinstance(ts, datetime):
                score = 0.0

            else:

                age_days = max(
                    (now - ts).days,
                    1,
                )

                score = 1 / age_days

            scored.append((chunk, score))

        scored.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        return scored