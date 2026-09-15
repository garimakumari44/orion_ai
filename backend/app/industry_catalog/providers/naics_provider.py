"""
app/industry_catalog/providers/naics_provider.py

NAICS (North American Industry Classification System) provider.

Responsibilities:
- NAICS code lookup
- NAICS industry search
- NAICS taxonomy retrieval
- deterministic company classification when a NAICS code is supplied

The provider does not:
- access repositories
- persist records
- run research agents
- perform LLM-based classification
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import IndustryProvider


class NAICSProvider(IndustryProvider):
    """
    NAICS taxonomy provider.

    NAICS is a hierarchical classification system.

    Typical hierarchy:

        Sector
            Subsector
                Industry Group
                    NAICS Industry
                        National Industry
    """

    name = "naics"
    priority = 30

    def __init__(
        self,
        taxonomy: Optional[List[Dict[str, Any]]] = None,
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__()

        self.enabled = enabled

        self._taxonomy = taxonomy or self._default_taxonomy()

        self._by_code: Dict[str, Dict[str, Any]] = {}

        for item in self._taxonomy:
            code = item.get("code")

            if code is None:
                continue

            normalized_code = self._normalize_code(code)

            if normalized_code:
                self._by_code[normalized_code] = dict(item)

    # ========================================================================
    # Provider identity
    # ========================================================================

    @property
    def provider_name(self) -> str:
        return self.name

    # ========================================================================
    # Search
    # ========================================================================

    def search_industry(
        self,
        query: str,
        *,
        limit: int = 20,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search NAICS taxonomy by code or textual description.
        """

        if not query or not query.strip():
            return []

        query_normalized = query.strip().lower()

        results: List[Dict[str, Any]] = []

        for item in self._taxonomy:
            code = str(item.get("code", "")).lower()

            searchable = " ".join(
                [
                    str(item.get("industry") or ""),
                    str(item.get("description") or ""),
                    str(item.get("sector") or ""),
                    str(item.get("subsector") or ""),
                    str(item.get("industry_group") or ""),
                ]
            ).lower()

            if (
                query_normalized in code
                or query_normalized in searchable
            ):
                results.append(
                    self._normalize_result(item)
                )

            if len(results) >= limit:
                break

        return results

    # ========================================================================
    # Industry lookup
    # ========================================================================

    def get_industry(
        self,
        industry: str,
        
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Look up a NAICS industry by code or name.
        """

        if not industry or not industry.strip():
            return None

        value = industry.strip()

        # ------------------------------------------------------------
        # Direct NAICS code lookup
        # ------------------------------------------------------------

        normalized_code = self._normalize_code(value)

        if normalized_code in self._by_code:
            return self._normalize_result(
                self._by_code[normalized_code]
            )

        # ------------------------------------------------------------
        # Exact name lookup
        # ------------------------------------------------------------

        value_lower = value.lower()

        for item in self._taxonomy:
            industry_name = str(
                item.get("industry")
                or item.get("description")
                or ""
            ).strip()

            if industry_name.lower() == value_lower:
                return self._normalize_result(item)

        # ------------------------------------------------------------
        # Partial name lookup
        # ------------------------------------------------------------

        for item in self._taxonomy:
            searchable = " ".join(
                [
                    str(item.get("industry") or ""),
                    str(item.get("description") or ""),
                    str(item.get("sector") or ""),
                    str(item.get("subsector") or ""),
                ]
            ).lower()

            if value_lower in searchable:
                return self._normalize_result(item)

        return None

    # ========================================================================
    # Company classification
    # ========================================================================

    def classify_company(
        self,
        company: Optional[str] = None,
        *,
        ticker: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Classify a company when a NAICS code is supplied.

        Supported kwargs:

            naics_code="334111"

        The provider does not infer a NAICS code from the company name.
        """

        naics_code = kwargs.get("naics_code")

        if naics_code is None:
            naics_code = kwargs.get("naics")

        if naics_code is None:
            return None

        normalized_code = self._normalize_code(naics_code)

        item = self._by_code.get(normalized_code)

        if item is None:
            return None

        result = self._normalize_result(item)

        result["company"] = company
        result["ticker"] = ticker

        return result

    # ========================================================================
    # Taxonomy
    # ========================================================================

    def get_taxonomy(
        self,
        *,
        taxonomy: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Return NAICS taxonomy.
        """

        if taxonomy:
            normalized = taxonomy.strip().lower()

            if normalized not in {
                "naics",
                "north american industry classification system",
            }:
                return []

        return [
            self._normalize_result(item)
            for item in self._taxonomy
        ]

    # ========================================================================
    # Health
    # ========================================================================

    def health_check(self) -> bool:
        """
        Check provider availability.
        """

        return self.enabled and bool(self._taxonomy)

    # ========================================================================
    # Code normalization
    # ========================================================================

    @staticmethod
    def _normalize_code(code: Any) -> str:
        """
        Normalize NAICS code.

        NAICS codes are numeric strings with up to six digits.
        """

        if code is None:
            return ""

        value = str(code).strip()

        if not value:
            return ""

        if value.isdigit():
            return value

        return value.lower()

    # ========================================================================
    # Result normalization
    # ========================================================================

    @staticmethod
    def _normalize_result(
        item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert raw NAICS data into the common industry representation.
        """

        code = item.get("code")

        industry = (
            item.get("industry")
            or item.get("description")
        )

        result: Dict[str, Any] = {
            "industry": industry,
            "sub_industry": item.get("sub_industry"),
            "sector": item.get("sector"),
            "code": (
                NAICSProvider._normalize_code(code)
                if code is not None
                else None
            ),
            "classification": "NAICS",
            "classification_system": "NAICS",
            "source": "naics",
        }

        # Preserve NAICS hierarchy.
        for field in (
            "sector_code",
            "subsector",
            "subsector_code",
            "industry_group",
            "industry_group_code",
            "national_industry",
            "national_industry_code",
            "title",
        ):
            if field in item:
                result[field] = item[field]

        return result

    # ========================================================================
    # Default taxonomy
    # ========================================================================

    @staticmethod
    def _default_taxonomy() -> List[Dict[str, Any]]:
        """
        Small baseline taxonomy.

        This is intentionally not a complete NAICS database.

        In production, load the official NAICS dataset instead.
        """

        return [
            {
                "code": "334111",
                "industry": "Electronic Computer Manufacturing",
                "description": (
                    "Electronic Computer Manufacturing"
                ),
                "sector": "Manufacturing",
                "sector_code": "31-33",
                "subsector": "Computer and Electronic Product Manufacturing",
                "subsector_code": "334",
                "industry_group": "Computer and Peripheral Equipment Manufacturing",
                "industry_group_code": "3341",
            },
            {
                "code": "334112",
                "industry": "Computer Storage Device Manufacturing",
                "description": (
                    "Computer Storage Device Manufacturing"
                ),
                "sector": "Manufacturing",
                "sector_code": "31-33",
                "subsector": "Computer and Electronic Product Manufacturing",
                "subsector_code": "334",
                "industry_group": "Computer and Peripheral Equipment Manufacturing",
                "industry_group_code": "3341",
            },
            {
                "code": "334413",
                "industry": "Semiconductor and Related Device Manufacturing",
                "description": (
                    "Semiconductor and Related Device Manufacturing"
                ),
                "sector": "Manufacturing",
                "sector_code": "31-33",
                "subsector": "Computer and Electronic Product Manufacturing",
                "subsector_code": "334",
                "industry_group": "Semiconductor and Other Electronic Component Manufacturing",
                "industry_group_code": "3344",
            },
            {
                "code": "511210",
                "industry": "Software Publishers",
                "description": "Software Publishers",
                "sector": "Information",
                "sector_code": "51",
                "subsector": "Publishing Industries",
                "subsector_code": "511",
                "industry_group": "Software Publishers",
                "industry_group_code": "5112",
            },
            {
                "code": "541511",
                "industry": "Custom Computer Programming Services",
                "description": (
                    "Custom Computer Programming Services"
                ),
                "sector": "Professional, Scientific, and Technical Services",
                "sector_code": "54",
                "subsector": "Professional, Scientific, and Technical Services",
                "subsector_code": "541",
                "industry_group": "Professional, Scientific, and Technical Services",
                "industry_group_code": "5415",
            },
        ]