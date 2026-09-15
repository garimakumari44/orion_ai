from __future__ import annotations

from typing import Any


class CompanyConfidenceCalculator:
    """
    Calculates a confidence score for a company record.

    The score ranges from 0 to 100.
    """

    PROVIDER_WEIGHTS = {
        "manual": 100,
        "sec": 100,
        "openfigi": 95,
        "polygon": 90,
        "alpha_vantage": 85,
        "fmp": 85,
        "yahoo": 75,
        "unknown": 50,
    }

    @classmethod
    def calculate(cls, data: dict[str, Any]) -> int:
        """
        Calculate a confidence score based on the provider and
        completeness of the record.
        """

        provider = str(
            data.get("primary_source", "unknown")
        ).lower()

        score = cls.PROVIDER_WEIGHTS.get(
            provider,
            cls.PROVIDER_WEIGHTS["unknown"],
        )

        # Bonus for important identifiers
        if data.get("figi"):
            score += 2

        if data.get("isin"):
            score += 2

        if data.get("lei"):
            score += 2

        if data.get("cik"):
            score += 2

        # Bonus for completeness
        important_fields = [
            "website",
            "description",
            "sector",
            "industry",
            "country",
            "exchange",
            "logo_url",
        ]

        completed = sum(
            1 for field in important_fields if data.get(field)
        )

        score += completed

        return min(score, 100)