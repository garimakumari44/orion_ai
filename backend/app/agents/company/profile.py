
"""
app/agents/company/profile.py

Analyzes and structures basic company information.

Responsibility:
    - Consume researched company-profile facts.
    - Normalize company identity fields.
    - Assess profile completeness.
    - Identify missing critical profile information.
    - Preserve the original researched facts.

This class does NOT perform external research or retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List


class CompanyProfileAnalyzer:
    """
    Analyzes basic company profile information.

    Expected researched input may contain:

        company_name
        description
        industry
        sector
        headquarters
        founded_year
        employees
        website
        ticker
    """

    def analyze(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze researched company profile data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        # =====================================================
        # Researched facts
        # =====================================================

        company_name = (
            data.get("company_name")
            or data.get("company")
        )

        description = data.get(
            "description"
        )

        industry = data.get(
            "industry"
        )

        sector = data.get(
            "sector"
        )

        headquarters = data.get(
            "headquarters"
        )

        founded_year = data.get(
            "founded_year"
        )

        employees = data.get(
            "employees"
        )

        website = data.get(
            "website"
        )

        ticker = data.get(
            "ticker"
        )

        # =====================================================
        # Derived analysis
        # =====================================================

        profile_completeness = (
            self._calculate_completeness(
                company_name=company_name,
                description=description,
                industry=industry,
                sector=sector,
                headquarters=headquarters,
                founded_year=founded_year,
                employees=employees,
                website=website,
                ticker=ticker,
            )
        )

        missing_information = (
            self._identify_missing_information(
                company_name=company_name,
                description=description,
                industry=industry,
                sector=sector,
                headquarters=headquarters,
                founded_year=founded_year,
                employees=employees,
                website=website,
                ticker=ticker,
            )
        )

        company_age = (
            self._calculate_company_age(
                founded_year
            )
        )

        company_scale = (
            self._assess_company_scale(
                employees
            )
        )

        identity_quality = (
            self._assess_identity_quality(
                company_name=company_name,
                ticker=ticker,
                industry=industry,
                sector=sector,
            )
        )

        # =====================================================
        # Result
        # =====================================================

        return {
            # -------------------------------------------------
            # Researched facts
            # -------------------------------------------------

            "company_name": company_name,

            "description": description,

            "industry": industry,

            "sector": sector,

            "headquarters": headquarters,

            "founded_year": founded_year,

            "employees": employees,

            "website": website,

            "ticker": ticker,

            # -------------------------------------------------
            # Derived analysis
            # -------------------------------------------------

            "profile_completeness": (
                profile_completeness
            ),

            "missing_information": (
                missing_information
            ),

            "company_age": company_age,

            "company_scale": company_scale,

            "identity_quality": identity_quality,

            "analysis_status": "completed",
        }

    # =========================================================
    # Profile Completeness
    # =========================================================

    @staticmethod
    def _calculate_completeness(
        company_name: Any,
        description: Any,
        industry: Any,
        sector: Any,
        headquarters: Any,
        founded_year: Any,
        employees: Any,
        website: Any,
        ticker: Any,
    ) -> Dict[str, Any]:
        """
        Calculate how complete the available company profile is.

        This measures information availability, not company quality.
        """

        fields = {
            "company_name": company_name,
            "description": description,
            "industry": industry,
            "sector": sector,
            "headquarters": headquarters,
            "founded_year": founded_year,
            "employees": employees,
            "website": website,
            "ticker": ticker,
        }

        available = [
            key
            for key, value in fields.items()
            if value is not None
            and value != ""
            and value != []
        ]

        total = len(fields)

        percentage = (
            len(available) / total * 100
            if total
            else 0
        )

        return {
            "available_fields": len(
                available
            ),
            "total_fields": total,
            "percentage": round(
                percentage,
                2,
            ),
        }

    # =========================================================
    # Missing Information
    # =========================================================

    @staticmethod
    def _identify_missing_information(
        company_name: Any,
        description: Any,
        industry: Any,
        sector: Any,
        headquarters: Any,
        founded_year: Any,
        employees: Any,
        website: Any,
        ticker: Any,
    ) -> List[str]:
        """
        Identify missing profile fields.

        These can later be used by the research layer to
        trigger targeted retrieval.
        """

        fields = {
            "company_name": company_name,
            "description": description,
            "industry": industry,
            "sector": sector,
            "headquarters": headquarters,
            "founded_year": founded_year,
            "employees": employees,
            "website": website,
            "ticker": ticker,
        }

        return [
            key
            for key, value in fields.items()
            if value is None
            or value == ""
            or value == []
        ]

    # =========================================================
    # Company Age
    # =========================================================

    @staticmethod
    def _calculate_company_age(
        founded_year: Any,
    ) -> int | None:
        """
        Calculate approximate company age.

        Returns None if founded_year cannot be interpreted.
        """

        if founded_year is None:
            return None

        try:
            year = int(
                str(founded_year)
                .strip()
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

        current_year = 2026

        if (
            year <= 0
            or year > current_year
        ):
            return None

        return current_year - year

    # =========================================================
    # Company Scale
    # =========================================================

    @staticmethod
    def _assess_company_scale(
        employees: Any,
    ) -> str:
        """
        Classify approximate company scale based on employee
        count when available.

        This is a rough structural classification, not a
        formal company-size classification.
        """

        if employees is None:
            return "unknown"

        try:
            count = int(
                str(employees)
                .replace(",", "")
                .strip()
            )
        except (
            TypeError,
            ValueError,
        ):
            return "unknown"

        if count <= 0:
            return "unknown"

        if count < 100:
            return "small"

        if count < 1000:
            return "mid_sized"

        if count < 10000:
            return "large"

        return "very_large"

    # =========================================================
    # Identity Quality
    # =========================================================

    @staticmethod
    def _assess_identity_quality(
        company_name: Any,
        ticker: Any,
        industry: Any,
        sector: Any,
    ) -> str:
        """
        Assess whether enough identity information exists to
        reliably identify the company.
        """

        identity_fields = [
            company_name,
            ticker,
            industry,
            sector,
        ]

        available = sum(
            1
            for value in identity_fields
            if value is not None
            and value != ""
        )

        if not company_name:
            return "insufficient"

        if (
            company_name
            and ticker
            and (
                industry
                or sector
            )
        ):
            return "strong"

        if available >= 2:
            return "adequate"

        return "basic"

