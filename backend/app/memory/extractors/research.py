"""
Research Memory Extractor

Extracts reusable research findings from
papers, articles, reports, or generated analyses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from app.memory.extractors.base import BaseExtractor
from app.memory.models.memory import (
    Memory,
    MemoryType,
    MemoryContent,
    MemoryMetadata,
    MemorySource,
)
from app.memory.utils.helpers import generate_memory_id


class ResearchExtractor(BaseExtractor):
    """
    Converts research outputs into long-term memory.
    """

    def __init__(self):
        super().__init__("research")

    # ---------------------------------------------------------

    def extract(self, documents: List[Dict]) -> List[Memory]:
        """
        Expected format

        [
            {
                "title": "Transformer Paper",
                "summary": "...",
                "url": "...",
                "tags": ["llm", "attention"]
            }
        ]
        """

        memories: List[Memory] = []

        for doc in documents:

            summary = doc.get("summary", "").strip()

            if not summary:
                continue

            memory = Memory(
                id=generate_memory_id(),
                type=MemoryType.RESEARCH,
                source=MemorySource.RESEARCH,
                content=MemoryContent(
                    text=summary,
                ),
                metadata=MemoryMetadata(
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    importance=0.8,
                    confidence=0.95,
                    access_count=0,
                    tags=doc.get("tags", []),
                    extra={
                        "title": doc.get("title"),
                        "url": doc.get("url"),
                        "authors": doc.get("authors", []),
                        "extractor": "research",
                    },
                ),
            )

            memories.append(memory)

        return memories

    # ---------------------------------------------------------

    def extract_key_points(
        self,
        documents: List[Dict],
    ) -> List[str]:
        """
        Return concise research summaries.
        """

        points: List[str] = []

        for doc in documents:

            summary = doc.get("summary", "").strip()

            if summary:
                points.append(summary)

        return points

    # ---------------------------------------------------------

    def extract_topics(
        self,
        documents: List[Dict],
    ) -> List[str]:
        """
        Collect unique research topics.
        """

        topics = set()

        for doc in documents:

            for tag in doc.get("tags", []):

                topics.add(tag)

        return sorted(topics)