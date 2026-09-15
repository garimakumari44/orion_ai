
"""
app/agents/company/geography.py

Analyzes the geographic footprint of a company.

Responsibility:
    - Consume researched geographic facts.
    - Normalize missing values.
    - Derive useful geographic insights.
    - Identify geographic concentration and exposure.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List


class GeographyAnalyzer:
    """
    Analyzes a company's geographic footprint.

    Expected input may contain:

        headquarters
        operating_regions
        manufacturing_locations
        sales_regions
        international_exposure

    The research/retrieval layer is responsible for discovering
    these facts.
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze geographic company data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        headquarters = data.get("headquarters")

        operating_regions = self._as_list(
            data.get("operating_regions")
        )

        manufacturing_locations = self._as_list(
            data.get("manufacturing_locations")
        )

        sales_regions = self._as_list(
            data.get("sales_regions")
        )

        international_exposure = data.get(
            "international_exposure"
        )

        # -------------------------------------------------
        # Derived analysis
        # -------------------------------------------------

        geographic_presence_count = (
            len(operating_regions)
        )

        manufacturing_presence_count = (
            len(manufacturing_locations)
        )

        sales_presence_count = (
            len(sales_regions)
        )

        geographic_diversification = (
            self._assess_geographic_diversification(
                operating_regions=operating_regions,
                sales_regions=sales_regions,
            )
        )

        geographic_concentration = (
            self._assess_geographic_concentration(
                operating_regions=operating_regions,
                manufacturing_locations=manufacturing_locations,
                sales_regions=sales_regions,
            )
        )

        international_exposure_assessment = (
            self._assess_international_exposure(
                international_exposure,
                operating_regions,
                sales_regions,
            )
        )

        geographic_risks = (
            self._identify_geographic_risks(
                international_exposure=international_exposure,
                manufacturing_locations=manufacturing_locations,
                sales_regions=sales_regions,
                operating_regions=operating_regions,
            )
        )

        return {
            # -------------------------------------------------
            # Discovered facts
            # -------------------------------------------------

            "headquarters": headquarters,

            "operating_regions": operating_regions,

            "manufacturing_locations": (
                manufacturing_locations
            ),

            "sales_regions": sales_regions,

            "international_exposure": (
                international_exposure
            ),

            # -------------------------------------------------
            # Derived metrics
            # -------------------------------------------------

            "geographic_presence_count": (
                geographic_presence_count
            ),

            "manufacturing_presence_count": (
                manufacturing_presence_count
            ),

            "sales_presence_count": (
                sales_presence_count
            ),

            # -------------------------------------------------
            # Geographic analysis
            # -------------------------------------------------

            "geographic_diversification": (
                geographic_diversification
            ),

            "geographic_concentration": (
                geographic_concentration
            ),

            "international_exposure_assessment": (
                international_exposure_assessment
            ),

            "geographic_risks": geographic_risks,

            # -------------------------------------------------
            # Analysis status
            # -------------------------------------------------

            "analysis_status": "completed",
        }

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """
        Normalize a potentially missing list field.

        Never fabricate geographic information.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    # =========================================================
    # Geographic Diversification
    # =========================================================

    @staticmethod
    def _assess_geographic_diversification(
        operating_regions: List[Any],
        sales_regions: List[Any],
    ) -> str:
        """
        Assess broad geographic diversification based on
        available regional information.

        This is a heuristic, not a factual claim.
        """

        regions = set()

        for region in operating_regions:
            if region:
                regions.add(str(region).strip().lower())

        for region in sales_regions:
            if region:
                regions.add(str(region).strip().lower())

        count = len(regions)

        if count == 0:
            return "unknown"

        if count == 1:
            return "low"

        if count <= 3:
            return "moderate"

        return "high"

    # =========================================================
    # Geographic Concentration
    # =========================================================

    @staticmethod
    def _assess_geographic_concentration(
        operating_regions: List[Any],
        manufacturing_locations: List[Any],
        sales_regions: List[Any],
    ) -> str:
        """
        Identify potential geographic concentration.

        This does not claim revenue or production concentration
        unless the underlying data explicitly provides it.
        """

        total_information = (
            len(operating_regions)
            + len(manufacturing_locations)
            + len(sales_regions)
        )

        if total_information == 0:
            return "unknown"

        if (
            len(operating_regions) <= 1
            or len(manufacturing_locations) <= 1
        ):
            return "potentially_concentrated"

        return "diversified"

    # =========================================================
    # International Exposure
    # =========================================================

    @staticmethod
    def _assess_international_exposure(
        international_exposure: Any,
        operating_regions: List[Any],
        sales_regions: List[Any],
    ) -> str:
        """
        Assess international exposure from explicitly supplied
        information.

        Prefer the supplied exposure value when available.
        """

        if international_exposure is not None:

            if isinstance(
                international_exposure,
                bool,
            ):
                return (
                    "high"
                    if international_exposure
                    else "low"
                )

            return str(
                international_exposure
            )

        if len(sales_regions) > 1:
            return "potentially_high"

        if len(operating_regions) > 1:
            return "potentially_high"

        if sales_regions or operating_regions:
            return "potentially_moderate"

        return "unknown"

    # =========================================================
    # Geographic Risks
    # =========================================================

    @staticmethod
    def _identify_geographic_risks(
        international_exposure: Any,
        manufacturing_locations: List[Any],
        sales_regions: List[Any],
        operating_regions: List[Any],
    ) -> List[str]:
        """
        Identify potential geographic risks.

        These are analytical flags, not claims that a risk
        definitely exists.
        """

        risks: List[str] = []

        # -------------------------------------------------
        # Manufacturing concentration
        # -------------------------------------------------

        if len(manufacturing_locations) == 1:
            risks.append(
                "Potential manufacturing concentration risk"
            )

        # -------------------------------------------------
        # Sales concentration
        # -------------------------------------------------

        if len(sales_regions) == 1:
            risks.append(
                "Potential sales-region concentration risk"
            )

        # -------------------------------------------------
        # International exposure
        # -------------------------------------------------

        if isinstance(
            international_exposure,
            str,
        ):
            exposure = (
                international_exposure.lower()
            )

            if exposure in {
                "high",
                "significant",
                "very_high",
            }:
                risks.append(
                    "Potential exposure to international "
                    "regulatory, currency, and geopolitical risks"
                )

        elif international_exposure is True:
            risks.append(
                "Potential exposure to international "
                "regulatory, currency, and geopolitical risks"
            )

        # -------------------------------------------------
        # Operating concentration
        # -------------------------------------------------

        if len(operating_regions) == 1:
            risks.append(
                "Potential geographic operating concentration"
            )

        return risks
