"""
Entity Memory Extractor

Extracts named entities from text.

Initially uses rule-based extraction.

Later this can be replaced by:
- spaCy
- GLiNER
- LLM extraction
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List, Set

from app.memory.extractors.base import BaseExtractor
from app.memory.models.memory import (
    Memory,
    MemoryType,
    MemoryContent,
    MemoryMetadata,
    MemorySource,
)
from app.memory.utils.helpers import generate_memory_id


class EntityExtractor(BaseExtractor):

    ENTITY_PATTERN = re.compile(
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
    )

    def __init__(self):
        super().__init__("entity")

    def extract(self, messages: List[Dict]) -> List[Memory]:

        memories: List[Memory] = []

        discovered: Set[str] = set()

        for message in messages:

            text = message.get("content", "").strip()

            if not text:
                continue

            for entity in self.ENTITY_PATTERN.findall(text):

                if len(entity) < 3:
                    continue

                if entity in discovered:
                    continue

                discovered.add(entity)

                memories.append(
                    Memory(
                        id=generate_memory_id(),
                        type=MemoryType.ENTITY,
                        source=MemorySource.USER,
                        content=MemoryContent(
                            text=entity,
                        ),
                        metadata=MemoryMetadata(
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            importance=0.6,
                            confidence=0.9,
                            access_count=0,
                            tags=["entity"],
                            extra={
                                "text": text,
                                "extractor": "entity",
                            },
                        ),
                    )
                )

        return memories

    def extract_entities(self, text: str) -> List[str]:
        """
        Return extracted entities only.
        """

        return list(
            {
                entity
                for entity in self.ENTITY_PATTERN.findall(text)
                if len(entity) >= 3
            }
        )