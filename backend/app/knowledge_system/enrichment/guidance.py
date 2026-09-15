from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.knowledge_system.types import KnowledgeItem

logger = logging.getLogger(__name__)


class GuidanceExtractor:
    """
    Extracts forward-looking guidance from knowledge items.

    Examples:

    Revenue guidance:
        "Revenue expected between $80B-$82B"

    EPS guidance:
        "EPS forecast increased to $6.20"

    Strategy guidance:
        "Management expects AI revenue growth to accelerate"
    """

    GUIDANCE_TYPES = {
        "REVENUE",
        "EPS",
        "GROWTH",
        "MARGIN",
        "CAPEX",
        "STRATEGY",
        "MARKET_OUTLOOK",
        "ECONOMIC_FORECAST",
        "OTHER",
    }


    def __init__(
        self,
        llm_service: Optional[Any] = None
    ):
        self.llm_service = llm_service



    def extract(
        self,
        item: KnowledgeItem
    ) -> List[Dict[str, Any]]:
        """
        Extract guidance statements.
        """

        try:

            text = self._get_text(item)

            if not text:
                return []


            if self.llm_service:
                return self._extract_with_llm(
                    text
                )


            return self._basic_extraction(
                text
            )


        except Exception as e:

            logger.exception(
                "Guidance extraction failed: %s",
                e
            )

            return []



    def _extract_with_llm(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Uses LLM for detailed guidance extraction.
        """

        prompt = f"""
Extract forward-looking guidance from this text.

Return JSON array only.

Each item must contain:

- guidance_type
- entity
- metric
- value
- timeframe
- direction
- confidence
- explanation


Text:

{text}
"""


        try:

            response = self.llm_service.generate(
                prompt
            )

            return self._normalize(
                response
            )


        except Exception as e:

            logger.warning(
                "LLM guidance extraction failed: %s",
                e
            )

            return []



    def _basic_extraction(
        self,
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Keyword based fallback.
        """

        guidance = []

        keywords = {
            "expects": "OTHER",
            "forecast": "MARKET_OUTLOOK",
            "guidance": "OTHER",
            "revenue": "REVENUE",
            "earnings": "EPS",
            "margin": "MARGIN",
            "growth": "GROWTH",
            "capex": "CAPEX",
        }


        lower = text.lower()


        detected = None


        for keyword, category in keywords.items():

            if keyword in lower:

                detected = category
                break



        if detected:

            guidance.append(
                {
                    "guidance_type": detected,

                    "entity": None,

                    "metric": None,

                    "value": None,

                    "timeframe": None,

                    "direction": "unknown",

                    "confidence": 0.5,

                    "explanation": text[:300],

                    "created_at":
                        datetime.utcnow().isoformat()
                }
            )


        return guidance



    def _normalize(
        self,
        data: Any
    ) -> List[Dict[str, Any]]:
        """
        Normalize LLM output.
        """

        if isinstance(data, dict):
            data = [data]


        results = []


        for item in data:

            if not isinstance(item, dict):
                continue


            guidance_type = (
                item.get(
                    "guidance_type"
                )
                or "OTHER"
            )


            if guidance_type not in self.GUIDANCE_TYPES:
                guidance_type = "OTHER"



            results.append(
                {
                    "guidance_type":
                        guidance_type,

                    "entity":
                        item.get(
                            "entity"
                        ),

                    "metric":
                        item.get(
                            "metric"
                        ),

                    "value":
                        item.get(
                            "value"
                        ),

                    "timeframe":
                        item.get(
                            "timeframe"
                        ),

                    "direction":
                        item.get(
                            "direction",
                            "unknown"
                        ),

                    "confidence":
                        item.get(
                            "confidence",
                            0.5
                        ),

                    "explanation":
                        item.get(
                            "explanation",
                            ""
                        ),

                    "created_at":
                        datetime.utcnow().isoformat()
                }
            )


        return results



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