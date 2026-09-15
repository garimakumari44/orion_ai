from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.knowledge_system.types import KnowledgeItem

logger = logging.getLogger(__name__)


class EventExtractor:
    """
    Extracts events from knowledge items.

    Responsibilities:
        - Identify important events
        - Normalize event structure
        - Create timeline information
        - Connect events with entities

    Example:

    Input:
        "Apple launched iPhone 17 on September 2026"

    Output:
        {
            "type": "PRODUCT_LAUNCH",
            "entity": "Apple",
            "date": "2026-09",
            "description": "Apple launched iPhone 17"
        }
    """

    EVENT_TYPES = {
        "EARNINGS",
        "ACQUISITION",
        "FUNDING",
        "PRODUCT_LAUNCH",
        "EXECUTIVE_CHANGE",
        "REGULATORY",
        "PARTNERSHIP",
        "LEGAL",
        "MARKET_EVENT",
        "ECONOMIC_EVENT",
        "OTHER",
    }

    def __init__(self, llm_service: Optional[Any] = None):
        self.llm_service = llm_service


    def extract(
        self,
        item: KnowledgeItem
    ) -> List[Dict[str, Any]]:
        """
        Extract events from a knowledge item.
        """

        try:
            text = self._get_text(item)

            if not text:
                return []

            if self.llm_service:
                return self._extract_with_llm(text)

            return self._basic_extraction(text)

        except Exception as e:
            logger.exception(
                "Event extraction failed: %s",
                e
            )

            return []


    def _extract_with_llm(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Uses LLM for advanced event extraction.
        """

        prompt = f"""
Extract important events from the following text.

Return JSON array only.

Each event must contain:

- event_type
- title
- description
- entities
- date
- importance

Text:

{text}
"""

        try:

            response = self.llm_service.generate(
                prompt
            )

            return self._normalize_events(
                response
            )

        except Exception as e:

            logger.warning(
                "LLM event extraction failed: %s",
                e
            )

            return []


    def _basic_extraction(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Lightweight fallback extraction.

        Used when no LLM is available.
        """

        events = []

        keywords = {
            "launch": "PRODUCT_LAUNCH",
            "acquired": "ACQUISITION",
            "merged": "ACQUISITION",
            "funding": "FUNDING",
            "appointed": "EXECUTIVE_CHANGE",
            "resigned": "EXECUTIVE_CHANGE",
            "approved": "REGULATORY",
            "lawsuit": "LEGAL",
            "earnings": "EARNINGS",
        }


        lower_text = text.lower()


        for keyword, event_type in keywords.items():

            if keyword in lower_text:

                events.append(
                    {
                        "event_type": event_type,
                        "title": keyword,
                        "description": text[:300],
                        "entities": [],
                        "date": None,
                        "importance": "medium",
                    }
                )


        return events


    def _normalize_events(
        self,
        events: Any
    ) -> List[Dict[str, Any]]:
        """
        Normalizes LLM output.
        """

        if isinstance(events, dict):
            events = [events]


        normalized = []


        for event in events:

            if not isinstance(event, dict):
                continue


            event_type = (
                event.get("event_type")
                or "OTHER"
            )


            if event_type not in self.EVENT_TYPES:
                event_type = "OTHER"


            normalized.append(
                {
                    "event_type": event_type,

                    "title":
                        event.get(
                            "title",
                            "Unknown event"
                        ),

                    "description":
                        event.get(
                            "description",
                            ""
                        ),

                    "entities":
                        event.get(
                            "entities",
                            []
                        ),

                    "date":
                        event.get(
                            "date"
                        ),

                    "importance":
                        event.get(
                            "importance",
                            "medium"
                        ),

                    "created_at":
                        datetime.utcnow().isoformat()
                }
            )


        return normalized


    def _get_text(
        self,
        item: KnowledgeItem
    ) -> str:
        """
        Extract text from KnowledgeItem.
        """

        if hasattr(item, "content"):
            return item.content


        if hasattr(item, "text"):
            return item.text


        if isinstance(item, dict):

            return (
                item.get("content")
                or item.get("text")
                or ""
            )


        return ""