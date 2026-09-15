"""
app/industry_catalog/providers/sic_provider.py

SIC (Standard Industrial Classification) provider.

This provider is intentionally self-contained and does not perform
database persistence.

The provider can operate from an in-memory SIC taxonomy and can later
be extended to load the taxonomy from:
- PostgreSQL
- JSON
- CSV
- government datasets
- an external API

SIC:
    Standard Industrial Classification.

Primary responsibilities:
- SIC code lookup
- SIC industry search
- SIC taxonomy retrieval
- basic company classification when an SIC code is supplied
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import IndustryProvider


class SICProvider(IndustryProvider):
    """
    SIC taxonomy provider.

    Provider priority is intentionally relatively high because SIC is
    a formal classification system and should be preferred over
    heuristic industry-name providers when an SIC code is available.
    """

    name = "sic"
    priority = 20

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
        Search SIC taxonomy by code or textual description.
        """

        if not query or not query.strip():
            return []

        query_normalized = query.strip().lower()

        results: List[Dict[str, Any]] = []

        for item in self._taxonomy:
            code = str(item.get("code", "")).lower()

            description = str(
                item.get("description")
                or item.get("industry")
                or ""
            ).lower()

            industry = str(
                item.get("industry")
                or ""
            ).lower()

            if (
                query_normalized in code
                or query_normalized in description
                or query_normalized in industry
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
        Look up a SIC industry by SIC code or exact/partial name.
        """

        if not industry or not industry.strip():
            return None

        value = industry.strip()

        # ------------------------------------------------------------
        # First: direct SIC code lookup
        # ------------------------------------------------------------

        normalized_code = self._normalize_code(value)

        if normalized_code in self._by_code:
            return self._normalize_result(
                self._by_code[normalized_code]
            )

        # ------------------------------------------------------------
        # Second: exact textual match
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
        # Third: partial textual match
        # ------------------------------------------------------------

        for item in self._taxonomy:
            searchable = " ".join(
                [
                    str(item.get("industry") or ""),
                    str(item.get("description") or ""),
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
        Classify a company when an SIC code is already supplied.

        This provider deliberately does NOT guess a company's SIC code
        from its name.

        Supported kwargs:

            sic_code="3571"

        This keeps classification deterministic.
        """

        sic_code = kwargs.get("sic_code")

        if sic_code is None:
            sic_code = kwargs.get("sic")

        if sic_code is None:
            return None

        normalized_code = self._normalize_code(sic_code)

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
        Return SIC taxonomy.

        If taxonomy is specified and is not SIC, return an empty list.
        """

        if taxonomy:
            normalized = taxonomy.strip().lower()

            if normalized not in {
                "sic",
                "standard industrial classification",
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
        SIC is currently backed by an in-memory taxonomy, so health is
        equivalent to provider availability.
        """

        return self.enabled and bool(self._taxonomy)

    # ========================================================================
    # Normalization
    # ========================================================================

    @staticmethod
    def _normalize_code(code: Any) -> str:
        """
        Normalize SIC codes.

        Examples:

            3571       -> "3571"
            "3571"     -> "3571"
            "03571"    -> "3571"
        """

        if code is None:
            return ""

        value = str(code).strip()

        if not value:
            return ""

        if value.isdigit():
            return value.lstrip("0") or "0"

        return value.lower()

    @staticmethod
    def _normalize_result(
        item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert raw SIC taxonomy data into the common industry format.
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
                SICProvider._normalize_code(code)
                if code is not None
                else None
            ),
            "classification": "SIC",
            "classification_system": "SIC",
            "source": "sic",
        }

        # Preserve optional hierarchy fields.
        for field in (
            "division",
            "major_group",
            "industry_group",
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

        This is intentionally not presented as a complete SIC database.
        Replace or extend this with your authoritative SIC dataset.
        """

        return [
            {
                "code": "3571",
                "industry": "Electronic Computers",
                "description": "Electronic Computers",
                "division": "D",
                "major_group": "35",
                "industry_group": "357",
            },
            {
                "code": "3572",
                "industry": "Computer Storage Devices",
                "description": "Computer Storage Devices",
                "division": "D",
                "major_group": "35",
                "industry_group": "357",
            },
            {
                "code": "3575",
                "industry": "Computer Terminals",
                "description": "Computer Terminals",
                "division": "D",
                "major_group": "35",
                "industry_group": "357",
            },
            {
                "code": "3674",
                "industry": "Semiconductors and Related Devices",
                "description": (
                    "Semiconductors and Related Device Manufacturing"
                ),
                "division": "D",
                "major_group": "36",
                "industry_group": "367",
            },
            {
                "code": "7372",
                "industry": "Prepackaged Software",
                "description": "Prepackaged Software",
                "division": "I",
                "major_group": "73",
                "industry_group": "737",
            },
            {
                "code": "7373",
                "industry": "Computer Integrated Systems Design",
                "description": (
                    "Computer Integrated Systems Design"
                ),
                "division": "I",
                "major_group": "73",
                "industry_group": "737",
            },
        ]