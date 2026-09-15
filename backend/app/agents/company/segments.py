
"""
app/agents/company/segments.py

Analyzes company business and revenue segments.

Responsibility:
    - Consume researched segment facts.
    - Normalize segment data.
    - Analyze segment breadth and concentration.
    - Compare available growth and profitability information.
    - Identify potential segment-related risks.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class SegmentAnalyzer:
    """
    Analyzes company business and revenue segments.

    Expected researched input may contain:

        business_segments
        revenue_segments
        segment_growth
        segment_profitability

    The research/retrieval layer is responsible for discovering
    these facts.
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze researched segment data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        # =====================================================
        # Researched facts
        # =====================================================

        business_segments = self._as_list(
            data.get("business_segments")
        )

        revenue_segments = self._as_list(
            data.get("revenue_segments")
        )

        segment_growth = self._as_list(
            data.get("segment_growth")
        )

        segment_profitability = self._as_list(
            data.get("segment_profitability")
        )

        # =====================================================
        # Derived analysis
        # =====================================================

        business_segment_count = len(
            business_segments
        )

        revenue_segment_count = len(
            revenue_segments
        )

        segment_breadth = (
            self._assess_segment_breadth(
                business_segments=business_segments,
                revenue_segments=revenue_segments,
            )
        )

        revenue_concentration = (
            self._assess_revenue_concentration(
                revenue_segments
            )
        )

        growth_assessment = (
            self._assess_segment_growth(
                segment_growth
            )
        )

        profitability_assessment = (
            self._assess_segment_profitability(
                segment_profitability
            )
        )

        segment_diversification = (
            self._assess_segment_diversification(
                business_segments=business_segments,
                revenue_segments=revenue_segments,
            )
        )

        segment_risks = (
            self._identify_segment_risks(
                business_segments=business_segments,
                revenue_segments=revenue_segments,
                segment_growth=segment_growth,
                segment_profitability=(
                    segment_profitability
                ),
            )
        )

        return {
            # -------------------------------------------------
            # Researched facts
            # -------------------------------------------------

            "business_segments": (
                business_segments
            ),

            "revenue_segments": (
                revenue_segments
            ),

            "segment_growth": (
                segment_growth
            ),

            "segment_profitability": (
                segment_profitability
            ),

            # -------------------------------------------------
            # Derived metrics
            # -------------------------------------------------

            "business_segment_count": (
                business_segment_count
            ),

            "revenue_segment_count": (
                revenue_segment_count
            ),

            # -------------------------------------------------
            # Segment analysis
            # -------------------------------------------------

            "segment_breadth": segment_breadth,

            "segment_diversification": (
                segment_diversification
            ),

            "revenue_concentration": (
                revenue_concentration
            ),

            "growth_assessment": (
                growth_assessment
            ),

            "profitability_assessment": (
                profitability_assessment
            ),

            "segment_risks": segment_risks,

            "analysis_status": "completed",
        }

    # =========================================================
    # Normalization
    # =========================================================

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """
        Normalize list-like segment data.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    # =========================================================
    # Segment Breadth
    # =========================================================

    @staticmethod
    def _assess_segment_breadth(
        business_segments: List[Any],
        revenue_segments: List[Any],
    ) -> str:
        """
        Assess the breadth of the company's disclosed
        business/revenue segments.
        """

        count = max(
            len(business_segments),
            len(revenue_segments),
        )

        if count == 0:
            return "unknown"

        if count == 1:
            return "single_segment"

        if count <= 3:
            return "moderate"

        return "broad"

    # =========================================================
    # Revenue Concentration
    # =========================================================

    @staticmethod
    def _assess_revenue_concentration(
        revenue_segments: List[Any],
    ) -> str:
        """
        Assess revenue concentration.

        If segment records contain actual revenue percentages,
        use those percentages.

        Otherwise, only provide a structural assessment and
        explicitly avoid claiming actual revenue concentration.
        """

        if not revenue_segments:
            return "unknown"

        percentages = (
            SegmentAnalyzer._extract_percentages(
                revenue_segments
            )
        )

        if percentages:

            largest = max(percentages)

            if largest >= 70:
                return "high"

            if largest >= 50:
                return "moderate_to_high"

            if largest >= 30:
                return "moderate"

            return "diversified"

        if len(revenue_segments) == 1:
            return "potentially_high"

        if len(revenue_segments) <= 2:
            return "potentially_moderate_to_high"

        return "unknown_without_revenue_weights"

    # =========================================================
    # Segment Growth
    # =========================================================

    @staticmethod
    def _assess_segment_growth(
        segment_growth: List[Any],
    ) -> Dict[str, Any]:
        """
        Analyze available segment growth information.

        Supports records such as:

            {
                "segment": "Cloud",
                "growth": 25
            }

        or:

            {
                "segment": "Cloud",
                "growth": "25%"
            }
        """

        if not segment_growth:
            return {
                "status": "unknown",
                "segments_with_growth_data": 0,
                "average_growth": None,
                "fastest_growing_segment": None,
                "slowest_growing_segment": None,
            }

        growth_records = []

        for item in segment_growth:

            if not isinstance(item, dict):
                continue

            segment = (
                item.get("segment")
                or item.get("name")
            )

            growth = (
                item.get("growth")
                if "growth" in item
                else item.get("growth_rate")
            )

            numeric_growth = (
                SegmentAnalyzer._percentage_value(
                    growth
                )
            )

            if numeric_growth is None:
                continue

            growth_records.append(
                {
                    "segment": segment,
                    "growth": numeric_growth,
                }
            )

        if not growth_records:
            return {
                "status": "data_present_but_uninterpretable",
                "segments_with_growth_data": 0,
                "average_growth": None,
                "fastest_growing_segment": None,
                "slowest_growing_segment": None,
            }

        average_growth = (
            sum(
                item["growth"]
                for item in growth_records
            )
            / len(growth_records)
        )

        fastest = max(
            growth_records,
            key=lambda item: item["growth"],
        )

        slowest = min(
            growth_records,
            key=lambda item: item["growth"],
        )

        return {
            "status": "available",
            "segments_with_growth_data": (
                len(growth_records)
            ),
            "average_growth": average_growth,
            "fastest_growing_segment": fastest,
            "slowest_growing_segment": slowest,
        }

    # =========================================================
    # Segment Profitability
    # =========================================================

    @staticmethod
    def _assess_segment_profitability(
        segment_profitability: List[Any],
    ) -> Dict[str, Any]:
        """
        Analyze available segment profitability information.

        Supports records such as:

            {
                "segment": "Cloud",
                "margin": 32
            }

        or:

            {
                "segment": "Cloud",
                "profit_margin": "32%"
            }
        """

        if not segment_profitability:
            return {
                "status": "unknown",
                "segments_with_profitability_data": 0,
                "average_margin": None,
                "highest_margin_segment": None,
                "lowest_margin_segment": None,
            }

        profitability_records = []

        for item in segment_profitability:

            if not isinstance(item, dict):
                continue

            segment = (
                item.get("segment")
                or item.get("name")
            )

            margin = (
                item.get("margin")
                if "margin" in item
                else item.get("profit_margin")
            )

            numeric_margin = (
                SegmentAnalyzer._percentage_value(
                    margin
                )
            )

            if numeric_margin is None:
                continue

            profitability_records.append(
                {
                    "segment": segment,
                    "margin": numeric_margin,
                }
            )

        if not profitability_records:
            return {
                "status": "data_present_but_uninterpretable",
                "segments_with_profitability_data": 0,
                "average_margin": None,
                "highest_margin_segment": None,
                "lowest_margin_segment": None,
            }

        average_margin = (
            sum(
                item["margin"]
                for item in profitability_records
            )
            / len(profitability_records)
        )

        highest = max(
            profitability_records,
            key=lambda item: item["margin"],
        )

        lowest = min(
            profitability_records,
            key=lambda item: item["margin"],
        )

        return {
            "status": "available",
            "segments_with_profitability_data": (
                len(profitability_records)
            ),
            "average_margin": average_margin,
            "highest_margin_segment": highest,
            "lowest_margin_segment": lowest,
        }

    # =========================================================
    # Segment Diversification
    # =========================================================

    @staticmethod
    def _assess_segment_diversification(
        business_segments: List[Any],
        revenue_segments: List[Any],
    ) -> str:
        """
        Assess structural segment diversification.
        """

        count = max(
            len(business_segments),
            len(revenue_segments),
        )

        if count == 0:
            return "unknown"

        if count == 1:
            return "low"

        if count <= 3:
            return "moderate"

        return "high"

    # =========================================================
    # Segment Risks
    # =========================================================

    @staticmethod
    def _identify_segment_risks(
        business_segments: List[Any],
        revenue_segments: List[Any],
        segment_growth: List[Any],
        segment_profitability: List[Any],
    ) -> List[str]:
        """
        Identify potential segment-related risks.

        These are analytical flags and should not be treated
        as definitive investment conclusions.
        """

        risks: List[str] = []

        # -----------------------------------------------------
        # Single segment
        # -----------------------------------------------------

        segment_count = max(
            len(business_segments),
            len(revenue_segments),
        )

        if segment_count == 1:
            risks.append(
                "Potential dependence on a single business segment"
            )

        if segment_count == 0:
            risks.append(
                "Business segment information unavailable"
            )

        # -----------------------------------------------------
        # Revenue concentration
        # -----------------------------------------------------

        revenue_concentration = (
            SegmentAnalyzer._assess_revenue_concentration(
                revenue_segments
            )
        )

        if revenue_concentration in {
            "high",
            "moderate_to_high",
        }:
            risks.append(
                "Potential revenue concentration in one segment"
            )

        # -----------------------------------------------------
        # Negative growth
        # -----------------------------------------------------

        for item in segment_growth:

            if not isinstance(item, dict):
                continue

            growth = (
                item.get("growth")
                if "growth" in item
                else item.get("growth_rate")
            )

            numeric_growth = (
                SegmentAnalyzer._percentage_value(
                    growth
                )
            )

            if (
                numeric_growth is not None
                and numeric_growth < 0
            ):
                segment = (
                    item.get("segment")
                    or item.get("name")
                    or "one or more segments"
                )

                risks.append(
                    f"Negative growth reported for "
                    f"segment: {segment}"
                )

        # -----------------------------------------------------
        # Low / negative profitability
        # -----------------------------------------------------

        for item in segment_profitability:

            if not isinstance(item, dict):
                continue

            margin = (
                item.get("margin")
                if "margin" in item
                else item.get("profit_margin")
            )

            numeric_margin = (
                SegmentAnalyzer._percentage_value(
                    margin
                )
            )

            if (
                numeric_margin is not None
                and numeric_margin < 0
            ):
                segment = (
                    item.get("segment")
                    or item.get("name")
                    or "one or more segments"
                )

                risks.append(
                    f"Negative profitability reported for "
                    f"segment: {segment}"
                )

        return risks

    # =========================================================
    # Percentage Parsing
    # =========================================================

    @staticmethod
    def _percentage_value(
        value: Any,
    ) -> Optional[float]:
        """
        Convert common percentage representations to a
        numeric percentage.

        Examples:

            25       -> 25.0
            0.25     -> 25.0
            "25%"    -> 25.0
            "25"     -> 25.0

        Returns None when the value cannot be interpreted.
        """

        if isinstance(value, bool):
            return None

        if isinstance(
            value,
            (int, float),
        ):
            number = float(value)

            if 0 <= number <= 1:
                return number * 100

            return number

        if isinstance(value, str):

            cleaned = (
                value
                .strip()
                .replace("%", "")
                .replace(",", "")
            )

            try:
                return float(cleaned)

            except ValueError:
                return None

        return None

    # =========================================================
    # Percentage Extraction
    # =========================================================

    @staticmethod
    def _extract_percentages(
        revenue_segments: List[Any],
    ) -> List[float]:
        """
        Extract revenue percentages from segment records.

        Supported keys:

            revenue_percentage
            revenue_share
            percentage
            share
        """

        percentages: List[float] = []

        for item in revenue_segments:

            if not isinstance(item, dict):
                continue

            value = None

            for key in (
                "revenue_percentage",
                "revenue_share",
                "percentage",
                "share",
            ):
                if key in item:
                    value = item[key]
                    break

            percentage = (
                SegmentAnalyzer._percentage_value(
                    value
                )
            )

            if percentage is not None:
                percentages.append(
                    percentage
                )

        return percentages

