"""
Conversation Memory Extractor

Extracts useful memories from user conversations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from app.memory.extractors.base import BaseExtractor
from app.memory.models.memory import (
    Memory,
    MemoryType,
    MemoryContent,
    MemoryMetadata,
    MemorySource,
)
from app.memory.utils.helpers import generate_memory_id


class ConversationExtractor(BaseExtractor):
    """
    Converts chat history into memory objects.
    """

    def __init__(self):
        super().__init__("conversation")

    # ---------------------------------------------------------

    def extract(self, messages: List[Dict[str, Any]]) -> List[Memory]:
        """
        Parameters
        ----------
        messages

        [
            {
                "role": "user",
                "content": "I prefer dark mode."
            },
            ...
        ]
        """

        memories: List[Memory] = []

        for message in messages:
            if message.get("role") != "user":
                continue

            text = message.get("content", "").strip()

            if not text:
                continue

            memory_type = self._classify(text)

            memory = Memory(
                id=generate_memory_id(),
                type=memory_type,
                source=MemorySource.USER,
                content=MemoryContent(
                    text=text,
                ),
                metadata=MemoryMetadata(
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    importance=0.5,
                    confidence=1.0,
                    access_count=0,
                    tags=[],
                    extra={
                        "length": len(text),
                        "extractor": "conversation",
                    },
                ),
            )

            memories.append(memory)

        return memories

    # ---------------------------------------------------------

    def _classify(self, text: str) -> MemoryType:
        """
        Very lightweight rule-based classifier.
        """

        lower = text.lower()

        preference_patterns = [
            "i like",
            "i prefer",
            "my favorite",
            "always",
            "never",
        ]

        project_patterns = [
            "building",
            "project",
            "working on",
            "creating",
        ]

        goal_patterns = [
            "i want",
            "goal",
            "planning",
            "target",
            "trying to",
        ]

        if any(pattern in lower for pattern in preference_patterns):
            return MemoryType.PREFERENCE

        if any(pattern in lower for pattern in project_patterns):
                   return MemoryType.SEMANTIC

        if any(pattern in lower for pattern in project_patterns):
                   return MemoryType.RESEARCH
        return MemoryType.CONVERSATION