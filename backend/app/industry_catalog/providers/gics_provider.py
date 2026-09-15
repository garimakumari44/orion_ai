"""
app/industry_catalog/providers/gics_provider.py

GICS (Global Industry Classification Standard) provider.

Responsibilities:
- GICS taxonomy lookup
- GICS industry search
- GICS taxonomy retrieval
- deterministic classification when GICS codes are supplied

This provider does not:
- persist data
- run research
- perform LLM research
- access repositories
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import IndustryProvider


class GICSProvider(IndustryProvider):
    """
    GICS taxonomy provider.

    GICS hierarchy:

        Sector
            Industry Group
                Industry
                    Sub-Industry
    """

    name = "gics"
    priority = 10

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
        Search GICS taxonomy by code or textual classification.
        """

        if not query or not query.strip():
            return []

        query = query.strip().lower()

        results: List[Dict[str, Any]] = []

        for item in self._taxonomy:
            code = str(item.get("code", "")).lower()

            searchable = " ".join(
                [
                    str(item.get("sector") or ""),
                    str(item.get("industry_group") or ""),
                    str(item.get("industry") or ""),
                    str(item.get("sub_industry") or ""),
                    str(item.get("description") or ""),
                ]
            ).lower()

            if query in code or query in searchable:
                results.append(
                    self._normalize_result(item)
                )

            if len(results) >= limit:
                break

        return results

    # ========================================================================
    # Lookup
    # ========================================================================

    def get_industry(
        self,
        industry: str,
        
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Look up a GICS classification by code or name.
        """

        if not industry or not industry.strip():
            return None

        value = industry.strip()

        code = self._normalize_code(value)

        if code in self._by_code:
            return self._normalize_result(
                self._by_code[code]
            )

        value_lower = value.lower()

        # Exact match.
        for item in self._taxonomy:
            names = [
                item.get("sector"),
                item.get("industry_group"),
                item.get("industry"),
                item.get("sub_industry"),
                item.get("description"),
            ]

            if any(
                str(name or "").strip().lower() == value_lower
                for name in names
            ):
                return self._normalize_result(item)

        # Partial match.
        for item in self._taxonomy:
            searchable = " ".join(
                [
                    str(item.get("sector") or ""),
                    str(item.get("industry_group") or ""),
                    str(item.get("industry") or ""),
                    str(item.get("sub_industry") or ""),
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
        Deterministically classify a company when a GICS code is supplied.

        Supported:

            gics_code="452020"

        The provider intentionally does not guess GICS from company name.
        """

        gics_code = kwargs.get("gics_code")

        if gics_code is None:
            gics_code = kwargs.get("gics")

        if gics_code is None:
            return None

        code = self._normalize_code(gics_code)

        item = self._by_code.get(code)

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
        Return GICS taxonomy.
        """

        if taxonomy:
            value = taxonomy.strip().lower()

            if value not in {
                "gics",
                "global industry classification standard",
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
        return self.enabled and bool(self._taxonomy)

    # ========================================================================
    # Helpers
    # ========================================================================

    @staticmethod
    def _normalize_code(code: Any) -> str:
        if code is None:
            return ""

        value = str(code).strip()

        if not value:
            return ""

        return value

    @staticmethod
    def _normalize_result(
        item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize GICS data into the canonical provider result shape.
        """

        return {
            "industry": (
                item.get("industry")
                or item.get("description")
            ),
            "sub_industry": item.get("sub_industry"),
            "sector": item.get("sector"),
            "code": (
                GICSProvider._normalize_code(item.get("code"))
                if item.get("code") is not None
                else None
            ),
            "classification": "GICS",
            "classification_system": "GICS",
            "source": "gics",

            "sector_code": item.get("sector_code"),
            "industry_group_code": item.get(
                "industry_group_code"
            ),
            "industry_code": item.get("industry_code"),
            "sub_industry_code": item.get(
                "sub_industry_code"
            ),
            "industry_group": item.get("industry_group"),
        }

    # ========================================================================
    # Baseline taxonomy
    # ========================================================================

    @staticmethod
    def _default_taxonomy() -> List[Dict[str, Any]]:
        """
        Small baseline GICS dataset.

        Replace with an authoritative licensed/current GICS dataset
        for production use.
        """

        return [
            {
                "code": "452020",
                "sector_code": "45",
                "sector": "Information Technology",
                "industry_group_code": "4520",
                "industry_group": "Technology Hardware & Equipment",
                "industry_code": "452020",
                "industry": "Technology Hardware, Storage & Peripherals",
                "sub_industry_code": "45202010",
                "sub_industry": "Technology Hardware, Storage & Peripherals",
            },
            {
                "code": "453010",
                "sector_code": "45",
                "sector": "Information Technology",
                "industry_group_code": "4530",
                "industry_group": "Semiconductors & Semiconductor Equipment",
                "industry_code": "453010",
                "industry": "Semiconductors & Semiconductor Equipment",
                "sub_industry_code": "45301010",
                "sub_industry": "Semiconductors",
            },
            {
                "code": "451020",
                "sector_code": "45",
                "sector": "Information Technology",
                "industry_group_code": "4510",
                "industry_group": "Software & Services",
                "industry_code": "451020",
                "industry": "Software",
                "sub_industry_code": "45102010",
                "sub_industry": "Systems Software",
            },
        ]