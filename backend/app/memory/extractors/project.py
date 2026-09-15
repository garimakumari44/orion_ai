"""
Project Memory Extractor

Extracts long-term information about user projects.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from app.memory.extractors.base import BaseExtractor
from app.memory.models.memory import Memory, MemoryType


class ProjectExtractor(BaseExtractor):
    """
    Extracts user project information into semantic memory.
    """

    KEYWORDS = [
        "building",
        "creating",
        "developing",
        "working on",
        "project",
        "startup",
        "system",
        "application",
        "platform",
    ]

    def __init__(self):
        super().__init__("project")

    def extract(self, messages: List[Dict]) -> List[Memory]:

        memories: List[Memory] = []

        for message in messages:

            if message.get("role") != "user":
                continue

            text = message.get("content", "").strip()

            if not text:
                continue

            lower = text.lower()

            matched_keywords = [
                keyword
                for keyword in self.KEYWORDS
                if keyword in lower
            ]

            if not matched_keywords:
                continue

            memories.append(
                Memory(
                    content=text,
                    memory_type=MemoryType.SEMANTIC,
                    source="conversation",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    metadata={
                        "category": "project",
                        "keywords": matched_keywords,
                    },
                )
            )

        return memories