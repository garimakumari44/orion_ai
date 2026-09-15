"""
Preference Memory Extractor

Extracts durable user preferences from conversations.
"""

from __future__ import annotations

import re
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


class PreferenceExtractor(BaseExtractor):
    """
    Extract user preferences from text.
    """

    PATTERNS = [
        r"\bi prefer (.+)",
        r"\bi like (.+)",
        r"\bi love (.+)",
        r"\bi always (.+)",
        r"\bi never (.+)",
        r"\bmy favorite (.+)",
    ]

    def __init__(self):
        super().__init__("preference")

    def extract(self, messages: List[Dict]) -> List[Memory]:

        memories: List[Memory] = []

        for message in messages:

            if message.get("role") != "user":
                continue

            text = message.get("content", "").strip()

            if not text:
                continue

            for pattern in self.PATTERNS:

                match = re.search(pattern, text, re.IGNORECASE)

                if not match:
                    continue

                value = match.group(1).strip()

                memories.append(
                    Memory(
                        id=generate_memory_id(),
                        type=MemoryType.PREFERENCE,
                        source=MemorySource.USER,
                        content=MemoryContent(
                            text=value,
                        ),
                        metadata=MemoryMetadata(
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            importance=0.7,
                            confidence=0.95,
                            access_count=0,
                            tags=["preference"],
                            extra={
                                "raw": text,
                                "pattern": pattern,
                                "extractor": "preference",
                            },
                        ),
                    )
                )

        return memories