"""
app/industry_catalog/processing/confidence.py

Deterministic confidence calculation for industry metadata.

Confidence is based on:
- availability of industry classification
- provider agreement
- classification codes
- provider authority
- sub-industry availability
- source diversity
"""

from __future__ import annotations

from typing import Any, Dict, List


class IndustryConfidenceCalculator:
    """
    Calculate confidence for resolved industry metadata.

    Returns a score between 0.0 and 1.0.
    """

    PROVIDER_WEIGHTS = {
        "sec": 1.00,
        "naics": 0.95,
        "sic": 0.95,
        "companies_house": 0.90,
        "openfigi": 0.85,
        "yahoo": 0.75,
        "polygon": 0.75,
        "alphavantage": 0.70,
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(
        self,
        resolved: Dict[str, Any],
        source_records: List[Dict[str, Any]],
    ) -> float:

        if not resolved:
            return 0.0

        score = 0.0

        # --------------------------------------------------------------
        # Industry exists.
        # --------------------------------------------------------------

        if resolved.get("industry"):
            score += 0.35
        else:
            return 0.0

        # --------------------------------------------------------------
        # Sub-industry.
        # --------------------------------------------------------------

        if resolved.get("sub_industry"):
            score += 0.10

        # --------------------------------------------------------------
        # SIC / NAICS classification.
        # --------------------------------------------------------------

        if resolved.get("sic_code"):
            score += 0.15

        if resolved.get("naics_code"):
            score += 0.15

        # --------------------------------------------------------------
        # Provider authority.
        # --------------------------------------------------------------

        provider_score = self._provider_score(
            source_records
        )

        score += provider_score * 0.15

        # --------------------------------------------------------------
        # Agreement.
        # --------------------------------------------------------------

        agreement = self._agreement_score(
            source_records
        )

        score += agreement * 0.10

        return round(
            min(score, 1.0),
            4,
        )

    # ------------------------------------------------------------------
    # Provider authority
    # ------------------------------------------------------------------

    def _provider_score(
        self,
        records: List[Dict[str, Any]],
    ) -> float:

        if not records:
            return 0.0

        scores = []

        for record in records:

            provider = str(
                record.get("provider")
                or ""
            ).lower()

            weight = self.PROVIDER_WEIGHTS.get(
                provider,
                0.50,
            )

            scores.append(weight)

        return max(scores) if scores else 0.0

    # ------------------------------------------------------------------
    # Agreement
    # ------------------------------------------------------------------

    def _agreement_score(
        self,
        records: List[Dict[str, Any]],
    ) -> float:

        industries = []

        for record in records:

            industry = record.get("industry")

            if industry:
                industries.append(
                    str(industry).strip().lower()
                )

        if not industries:
            return 0.0

        if len(industries) == 1:
            return 1.0

        unique = set(industries)

        if len(unique) == 1:
            return 1.0

        frequency = {}

        for industry in industries:
            frequency[industry] = (
                frequency.get(industry, 0) + 1
            )

        highest = max(
            frequency.values()
        )

        return highest / len(industries)