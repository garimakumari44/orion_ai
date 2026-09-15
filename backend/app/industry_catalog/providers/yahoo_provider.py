"""
app/industry_catalog/providers/yahoo_provider.py

Yahoo Finance industry metadata provider.

Responsibilities
----------------
- Retrieve company metadata from Yahoo Finance.
- Extract sector and industry.
- Extract related classification metadata.
- Normalize Yahoo Finance results into the Industry Catalog format.

This provider does NOT:
- persist data
- perform research
- calculate final industry confidence
- override authoritative classifications
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .base import IndustryProvider

logger = logging.getLogger(__name__)


class YahooIndustryProvider(IndustryProvider):
    """
    Yahoo Finance metadata provider.

    Expected dependency:

        YahooFinanceTool

    The dependency is injected so this provider does not construct
    application infrastructure itself.
    """

    name = "yahoo"
    priority = 50

    def __init__(
        self,
        yahoo_tool: Optional[Any] = None,
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__()

        self.enabled = enabled
        self.yahoo_tool = yahoo_tool

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
        Yahoo Finance is not treated as a taxonomy search engine.

        If a ticker is supplied, retrieve that company's industry metadata.
        """

        ticker = kwargs.get("ticker")

        if not ticker:
            return []

        result = self.classify_company(
            ticker=ticker,
            company=kwargs.get("company"),
        )

        if not result:
            return []

        return [result][:limit]

    # ========================================================================
    # Lookup
    # ========================================================================

    def get_industry(
        self,
        industry: str,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve industry information for a ticker.

        `industry` is interpreted as a ticker when no explicit ticker
        is supplied.
        """

        ticker = kwargs.get("ticker") or industry

        return self.classify_company(
            ticker=ticker,
            company=kwargs.get("company"),
        )

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
        Retrieve company industry metadata from Yahoo Finance.

        Returns a normalized flat dictionary suitable for the
        IndustryProviderManager.

        Example:

            {
                "company": "8x8, Inc.",
                "ticker": "EGHT",
                "industry": "Software - Application",
                "sub_industry": None,
                "sector": "Technology",
                "classification": "Yahoo Finance",
                "classification_system": "Yahoo Finance",
                "source": "yahoo",
                "confidence": 0.70
            }
        """

        if not ticker:
            logger.warning(
                "Yahoo industry classification requested without ticker"
            )
            return None

        if self.yahoo_tool is None:
            logger.warning(
                "YahooIndustryProvider has no YahooFinanceTool configured"
            )
            return None

        normalized_ticker = str(ticker).strip().upper()

        if not normalized_ticker:
            return None

        try:
            raw = self.yahoo_tool.execute(
                ticker=normalized_ticker,
                operation="overview",
            )

        except TypeError:
            # Compatibility with tools that accept ticker positionally.
            try:
                raw = self.yahoo_tool.execute(
                    normalized_ticker,
                    operation="overview",
                )
            except Exception:
                logger.exception(
                    "Yahoo Finance lookup failed for ticker '%s'",
                    normalized_ticker,
                )
                return None

        except Exception:
            logger.exception(
                "Yahoo Finance lookup failed for ticker '%s'",
                normalized_ticker,
            )
            return None

        if not isinstance(raw, dict):
            logger.warning(
                "Yahoo Finance returned invalid response type for ticker '%s': %s",
                normalized_ticker,
                type(raw).__name__,
            )
            return None

        # The YahooFinanceTool contract uses:
        #
        # {
        #     "success": True,
        #     "ticker": "...",
        #     "company": {
        #         "name": "...",
        #         "sector": "...",
        #         "industry": "..."
        #     }
        # }
        #
        # Do not attempt classification from a failed tool response.

        if raw.get("success") is False:
            logger.warning(
                "Yahoo Finance returned unsuccessful response for ticker '%s': %s",
                normalized_ticker,
                raw.get("error"),
            )
            return None

        return self._normalize_result(
            raw,
            company=company,
            ticker=normalized_ticker,
        )

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
        Yahoo Finance does not provide an authoritative taxonomy through
        this provider.

        Return [] rather than pretending Yahoo is a taxonomy authority.
        """

        return []

    # ========================================================================
    # Health
    # ========================================================================

    def health_check(self) -> bool:
        """
        Report whether the provider is configured and enabled.

        Actual Yahoo connectivity is delegated to YahooFinanceTool.
        """

        return (
            self.enabled
            and self.yahoo_tool is not None
        )

    # ========================================================================
    # Normalization
    # ========================================================================

    @staticmethod
    def _normalize_result(
        raw: Dict[str, Any],
        *,
        company: Optional[str],
        ticker: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Normalize the YahooFinanceTool overview response.

        Important:
        YahooFinanceTool returns company metadata nested under
        `raw["company"]`.

        This method intentionally converts that provider/tool response
        into the flat IndustryProvider contract.
        """

        if not isinstance(raw, dict):
            return None

        company_data = raw.get("company")

        if not isinstance(company_data, dict):
            company_data = {}

        # ------------------------------------------------------------------
        # Company name
        # ------------------------------------------------------------------

        company_name = (
            company_data.get("name")
            or raw.get("longName")
            or raw.get("shortName")
            or raw.get("company_name")
            or company
        )

        # ------------------------------------------------------------------
        # Sector
        # ------------------------------------------------------------------

        sector = (
            company_data.get("sector")
            or raw.get("sector")
            or raw.get("Sector")
        )

        # ------------------------------------------------------------------
        # Industry
        # ------------------------------------------------------------------

        industry = (
            company_data.get("industry")
            or raw.get("industry")
            or raw.get("Industry")
        )

        # ------------------------------------------------------------------
        # Sub-industry
        # ------------------------------------------------------------------

        sub_industry = (
            company_data.get("sub_industry")
            or company_data.get("subIndustry")
            or raw.get("sub_industry")
            or raw.get("subIndustry")
        )

        # A company classification without an industry is not useful
        # to the Industry Catalog.
        if not industry:
            logger.warning(
                "Yahoo Finance returned no industry classification: "
                "company=%r ticker=%r sector=%r",
                company_name,
                ticker,
                sector,
            )
            return None

        # ------------------------------------------------------------------
        # Stable normalized Industry Catalog contract
        # ------------------------------------------------------------------

        result: Dict[str, Any] = {
            "company": company_name,
            "ticker": ticker,

            "industry": industry,
            "sub_industry": sub_industry,
            "sector": sector,

            "classification": "Yahoo Finance",
            "classification_system": "Yahoo Finance",

            "source": "yahoo",
            "confidence": 0.70,
        }

        # ------------------------------------------------------------------
        # Preserve useful metadata
        # ------------------------------------------------------------------

        metadata_mapping = {
            "website": "website",
            "country": "country",
            "city": "city",
            "state": "state",
            "zip": "zip",
            "fullTimeEmployees": "employees",
            "longBusinessSummary": "description",
        }

        for source_key, target_key in metadata_mapping.items():
            value = company_data.get(source_key)

            if value is None:
                value = raw.get(source_key)

            if value is not None:
                result[target_key] = value

        # ------------------------------------------------------------------
        # Preserve the original Yahoo response for diagnostics.
        #
        # This is useful during provider debugging but does not change
        # the canonical classification fields.
        # ------------------------------------------------------------------

        result["_raw_source"] = "yahoo_finance"

        return result