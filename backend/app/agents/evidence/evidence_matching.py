"""
app/agents/evidence/evidence_matching.py

Evidence Matching Engine.

Maps research claims to supporting evidence sources.
"""

from __future__ import annotations

from typing import Any


class EvidenceMatcher:
    """
    Connects:

        Claim
          |
        Evidence
          |
        Source
    """

    async def match(
        self,
        claims: list[dict[str, Any]],
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Match claims against available sources.

        This remains a lightweight fallback matcher.

        EvidenceAgent performs stronger source association before
        calling this fallback.
        """

        results: list[dict[str, Any]] = []

        for claim in claims:

            if not isinstance(
                claim,
                dict,
            ):
                continue

            matched_source = self.find_source(
                claim,
                sources,
            )

            results.append(
                {
                    "claim": claim.get(
                        "text"
                    ),
                    "claim_data": claim,
                    "source": (
                        matched_source.get(
                            "name"
                        )
                        or matched_source.get(
                            "title"
                        )
                        or matched_source.get(
                            "provider"
                        )
                        if matched_source
                        else None
                    ),
                    "provider": (
                        matched_source.get(
                            "provider"
                        )
                        if matched_source
                        else None
                    ),
                    "url": (
                        matched_source.get(
                            "url"
                        )
                        if matched_source
                        else None
                    ),
                    "document": (
                        matched_source.get(
                            "document"
                        )
                        or matched_source.get(
                            "title"
                        )
                        if matched_source
                        else None
                    ),
                    "date": (
                        matched_source.get(
                            "date"
                        )
                        if matched_source
                        else None
                    ),
                    "content": (
                        matched_source.get(
                            "content"
                        )
                        or matched_source.get(
                            "excerpt"
                        )
                        or matched_source.get(
                            "description"
                        )
                        if matched_source
                        else None
                    ),
                    "confidence": self.calculate_confidence(
                        matched_source
                    ),
                }
            )

        return results

    async def verify(
        self,
        claim: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Verify that a claim contains actual evidence.
        """

        if not isinstance(
            claim,
            dict,
        ):
            return {
                "claim": claim,
                "verified": False,
                "reason": "Invalid claim format",
            }

        evidence = claim.get(
            "evidence"
        )

        if not evidence:
            return {
                "claim": claim,
                "verified": False,
                "reason": "No supporting evidence",
            }

        if isinstance(
            evidence,
            dict,
        ):
            has_source = bool(
                evidence.get(
                    "source"
                )
                or evidence.get(
                    "provider"
                )
                or evidence.get(
                    "url"
                )
            )
        else:
            has_source = bool(
                evidence
            )

        return {
            "claim": claim,
            "verified": has_source,
        }

    def find_source(
        self,
        claim: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """
        Lightweight keyword fallback.

        Prefer explicit source-agent relationships whenever
        possible.
        """

        if not isinstance(
            claim,
            dict,
        ):
            return None

        claim_agent = claim.get(
            "source_agent"
        )

        claim_text = str(
            claim.get(
                "text",
                ""
            )
        ).lower()

        # -----------------------------------------------------
        # First: source-agent relationship
        # -----------------------------------------------------

        if claim_agent:

            for source in sources:

                if not isinstance(
                    source,
                    dict,
                ):
                    continue

                if (
                    source.get(
                        "agent"
                    )
                    == claim_agent
                ):
                    return source

                if (
                    source.get(
                        "source_agent"
                    )
                    == claim_agent
                ):
                    return source

        # -----------------------------------------------------
        # Second: keyword fallback
        # -----------------------------------------------------

        keywords = [
            word
            for word in claim_text.split()
            if len(word) >= 4
        ]

        if not keywords:
            return None

        for source in sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            source_text = str(
                source
            ).lower()

            if any(
                word in source_text
                for word in keywords
            ):
                return source

        return None

    @staticmethod
    def calculate_confidence(
        source: dict[str, Any] | None,
    ) -> float:
        """
        Calculate source confidence.

        IMPORTANT:
            return 0.85
        NOT:
            return 0.85,
        """

        if not source:
            return 0.0

        return 0.85