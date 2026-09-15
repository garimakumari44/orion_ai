"""
Citation Manager

Creates structured citations for research claims.
"""

from __future__ import annotations

from typing import Any


class CitationManager:
    """
    Handles:

    - Citation creation
    - Citation formatting
    - Source linking
    """

    async def create(
        self,
        evidence_items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Create structured citations from evidence.
        """

        citations: list[dict[str, Any]] = []

        for item in evidence_items:

            if not isinstance(
                item,
                dict,
            ):
                continue

            citation = {
                "claim": item.get(
                    "claim"
                ),
                "source": (
                    item.get(
                        "source"
                    )
                    or item.get(
                        "provider"
                    )
                ),
                "document": item.get(
                    "document"
                ),
                "url": item.get(
                    "url"
                ),
                "date": item.get(
                    "date"
                ),
                "confidence": item.get(
                    "confidence",
                    0.0,
                ),
            }

            citations.append(
                citation
            )

        return citations

    def format_citation(
        self,
        citation: dict[str, Any],
    ) -> str:
        """
        Format citation as a string.

        IMPORTANT:
        Do not put a trailing comma after the return
        expression.
        """

        source = (
            citation.get(
                "source"
            )
            or citation.get(
                "provider"
            )
            or "Unknown Source"
        )

        document = (
            citation.get(
                "document"
            )
            or citation.get(
                "url"
            )
            or "Unknown Document"
        )

        return (
            f"{source} - "
            f"{document}"
        )