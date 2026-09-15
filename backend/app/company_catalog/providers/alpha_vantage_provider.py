"""
app/company_catalog/providers/alpha_vantage_provider.py

Alpha Vantage Provider.

Responsibilities
----------------
- Retrieve company profiles from Alpha Vantage.
- Preserve useful Alpha Vantage company metadata.
- Normalize Alpha Vantage fields into the canonical
  company structure.
- Preserve explicit sector / industry classification.
- Never infer industry from sector.

Current Scope
-------------
Alpha Vantage is used only for company profile enrichment.

The provider does NOT perform company discovery.

Configuration
-------------
API key:

    ALPHA_VANTAGE_API_KEY

The key may also be supplied directly to the constructor,
which is useful for tests.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import BaseProvider


logger = logging.getLogger(__name__)


class AlphaVantageProvider(BaseProvider):
    """
    Alpha Vantage company profile provider.

    Alpha Vantage's OVERVIEW endpoint provides:
    - company identity
    - classification
    - business description
    - exchange information
    - country/currency
    - fundamental/company metrics

    The original Alpha Vantage response is preserved in
    `provider_data`.
    """

    name = "alpha_vantage"

    BASE_URL = "https://www.alphavantage.co/query"

    DEFAULT_TIMEOUT = 10

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize Alpha Vantage.

        Parameters
        ----------
        api_key:
            Optional Alpha Vantage API key.

            When omitted, the provider reads:

                ALPHA_VANTAGE_API_KEY

        timeout:
            HTTP timeout in seconds.
        """

        self.api_key = (
            api_key
            or os.getenv("ALPHA_VANTAGE_API_KEY")
            or ""
        ).strip()

        try:
            self.timeout = max(int(timeout), 1)
        except (TypeError, ValueError):
            self.timeout = self.DEFAULT_TIMEOUT

    # =========================================================
    # Search Companies
    # =========================================================

    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Alpha Vantage is intentionally not used for discovery.

        Company discovery should be handled by dedicated
        discovery providers such as Yahoo or other catalog
        sources.
        """

        return []

    # =========================================================
    # List Companies
    # =========================================================

    async def list_companies(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Alpha Vantage does not provide the catalog behavior
        required by the company provider abstraction.

        Bulk catalog ingestion should be handled by a
        dedicated symbol-universe/synchronization service.
        """

        return []

    # =========================================================
    # Company Profile
    # =========================================================

    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve a complete company profile from Alpha Vantage.

        Uses:

            function=OVERVIEW

        Important classification rule:

            Sector -> sector
            Industry -> industry

        Industry is NEVER inferred from Sector.
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "Alpha Vantage company symbol must be a string."
            )

        symbol = symbol.strip().upper()

        if not symbol:
            return {}

        # -----------------------------------------------------
        # Configuration
        # -----------------------------------------------------

        if not self.api_key:
            logger.warning(
                "Alpha Vantage API key is not configured."
            )

            return self._minimal_result(symbol)

        try:
            response = await self._request_overview(symbol)

            if not response:
                return self._minimal_result(symbol)

            if not isinstance(response, dict):
                logger.warning(
                    "Alpha Vantage returned invalid response type | "
                    "type=%s | symbol=%s",
                    type(response).__name__,
                    symbol,
                )

                return self._minimal_result(symbol)

            # -------------------------------------------------
            # Error / rate-limit response
            # -------------------------------------------------

            if self._is_error_response(response):
                logger.warning(
                    "Alpha Vantage returned an error/information "
                    "response | symbol=%s | response=%r",
                    symbol,
                    response,
                )

                return self._minimal_result(symbol)

            # -------------------------------------------------
            # Preserve complete provider payload
            # -------------------------------------------------

            result: dict[str, Any] = dict(response)

            result["source"] = self.name

            result["provider_data"] = dict(response)

            # -------------------------------------------------
            # Identity
            # -------------------------------------------------

            self._set_if_present(
                result,
                "name",
                self._first_value(
                    response,
                    "Name",
                    "name",
                ),
            )

            resolved_symbol = (
                self._first_value(
                    response,
                    "Symbol",
                    "symbol",
                )
                or symbol
            )

            result["symbol"] = str(
                resolved_symbol
            ).strip().upper()

            result["ticker"] = result["symbol"]

            self._set_if_present(
                result,
                "exchange",
                self._first_value(
                    response,
                    "Exchange",
                    "exchange",
                ),
            )

            self._set_if_present(
                result,
                "country",
                self._first_value(
                    response,
                    "Country",
                    "country",
                ),
            )

            self._set_if_present(
                result,
                "currency",
                self._first_value(
                    response,
                    "Currency",
                    "currency",
                ),
            )

            self._set_if_present(
                result,
                "cik",
                self._normalize_cik(
                    self._first_value(
                        response,
                        "CIK",
                        "cik",
                    )
                ),
            )

            # -------------------------------------------------
            # Company information
            # -------------------------------------------------

            self._set_if_present(
                result,
                "description",
                self._first_value(
                    response,
                    "Description",
                    "description",
                ),
            )

            self._set_if_present(
                result,
                "address",
                self._first_value(
                    response,
                    "Address",
                    "address",
                ),
            )

            self._set_if_present(
                result,
                "fiscal_year_end",
                self._first_value(
                    response,
                    "FiscalYearEnd",
                    "fiscal_year_end",
                ),
            )

            self._set_if_present(
                result,
                "latest_quarter",
                self._first_value(
                    response,
                    "LatestQuarter",
                    "latest_quarter",
                ),
            )

            self._set_if_present(
                result,
                "asset_type",
                self._first_value(
                    response,
                    "AssetType",
                    "asset_type",
                ),
            )

            # -------------------------------------------------
            # Classification
            # -------------------------------------------------
            #
            # IMPORTANT:
            #
            # Sector and Industry remain separate.
            #
            # NEVER:
            #
            #     industry = sector
            #
            # Industry comes only from the explicit
            # Alpha Vantage Industry field.
            # -------------------------------------------------

            self._set_if_present(
                result,
                "sector",
                self._first_value(
                    response,
                    "Sector",
                    "sector",
                ),
            )

            self._set_if_present(
                result,
                "industry",
                self._first_value(
                    response,
                    "Industry",
                    "industry",
                ),
            )

            # -------------------------------------------------
            # Financial/company metadata
            # -------------------------------------------------

            canonical_numeric_fields: dict[
                str,
                tuple[str, ...],
            ] = {
                "market_capitalization": (
                    "MarketCapitalization",
                ),
                "ebitda": (
                    "EBITDA",
                ),
                "pe_ratio": (
                    "PERatio",
                ),
                "peg_ratio": (
                    "PEGRatio",
                ),
                "book_value": (
                    "BookValue",
                ),
                "dividend_per_share": (
                    "DividendPerShare",
                ),
                "dividend_yield": (
                    "DividendYield",
                ),
                "eps": (
                    "EPS",
                ),
                "revenue_per_share_ttm": (
                    "RevenuePerShareTTM",
                ),
                "profit_margin": (
                    "ProfitMargin",
                ),
                "operating_margin_ttm": (
                    "OperatingMarginTTM",
                ),
                "return_on_assets_ttm": (
                    "ReturnOnAssetsTTM",
                ),
                "return_on_equity_ttm": (
                    "ReturnOnEquityTTM",
                ),
                "revenue_ttm": (
                    "RevenueTTM",
                ),
                "gross_profit_ttm": (
                    "GrossProfitTTM",
                ),
                "diluted_eps_ttm": (
                    "DilutedEPSTTM",
                ),
                "quarterly_earnings_growth_yoy": (
                    "QuarterlyEarningsGrowthYOY",
                ),
                "quarterly_revenue_growth_yoy": (
                    "QuarterlyRevenueGrowthYOY",
                ),
                "analyst_target_price": (
                    "AnalystTargetPrice",
                ),
            }

            for canonical_field, provider_fields in (
                canonical_numeric_fields.items()
            ):
                value = self._first_value(
                    response,
                    *provider_fields,
                )

                if self._has_value(value):
                    result[canonical_field] = value

            # -------------------------------------------------
            # Analyst ratings
            # -------------------------------------------------

            analyst_fields = (
                "AnalystRatingStrongBuy",
                "AnalystRatingBuy",
                "AnalystRatingHold",
                "AnalystRatingSell",
                "AnalystRatingStrongSell",
            )

            analyst_ratings: dict[str, Any] = {}

            for field in analyst_fields:
                value = response.get(field)

                if self._has_value(value):
                    analyst_ratings[field] = value

            if analyst_ratings:
                result["analyst_ratings"] = analyst_ratings

            return result

        except Exception:
            logger.exception(
                "Alpha Vantage profile request failed | symbol=%s",
                symbol,
            )

            return self._minimal_result(symbol)

    # =========================================================
    # HTTP Request
    # =========================================================

    async def _request_overview(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Request Alpha Vantage OVERVIEW.

        urllib is executed inside asyncio.to_thread()
        so this provider remains asynchronous without
        introducing another HTTP dependency.
        """

        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key,
        }

        url = (
            f"{self.BASE_URL}?"
            f"{urlencode(params)}"
        )

        return await asyncio.to_thread(
            self._request_json,
            url,
            self.timeout,
        )

    @staticmethod
    def _request_json(
        url: str,
        timeout: int,
    ) -> dict[str, Any]:
        """
        Execute a synchronous JSON request.

        This method runs inside a worker thread.
        """

        request = Request(
            url,
            headers={
                "User-Agent": (
                    "EnterpriseCompanyCatalog/1.0"
                ),
                "Accept": "application/json",
            },
        )

        with urlopen(
            request,
            timeout=timeout,
        ) as response:
            raw = response.read()

        data = json.loads(
            raw.decode("utf-8")
        )

        if not isinstance(data, dict):
            return {}

        return data

    # =========================================================
    # Error Detection
    # =========================================================

    @staticmethod
    def _is_error_response(
        response: dict[str, Any],
    ) -> bool:
        """
        Detect Alpha Vantage error/information responses.

        Alpha Vantage may return:
            Error Message
            Information
            Note
        instead of overview data.
        """

        error_fields = (
            "Error Message",
            "error",
            "error_message",
        )

        for field in error_fields:
            if AlphaVantageProvider._has_value(
                response.get(field)
            ):
                return True

        if AlphaVantageProvider._has_value(
            response.get("Information")
        ):
            return True

        if AlphaVantageProvider._has_value(
            response.get("Note")
        ):
            return True

        return False

    # =========================================================
    # Value Helpers
    # =========================================================

    @staticmethod
    def _first_value(
        data: dict[str, Any] | None,
        *fields: str,
    ) -> Any:
        """
        Return the first meaningful value.
        """

        if not isinstance(data, dict):
            return None

        for field in fields:
            value = data.get(field)

            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()

                if not value:
                    continue

            return value

        return None

    @staticmethod
    def _set_if_present(
        target: dict[str, Any],
        field: str,
        value: Any,
    ) -> None:
        """
        Set a canonical field only when populated.
        """

        if value is None:
            return

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return

        target[field] = value

    @staticmethod
    def _normalize_cik(
        value: Any,
    ) -> str | None:
        """
        Normalize an Alpha Vantage CIK value.
        """

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        if value.isdigit():
            normalized = value.lstrip("0")
            return normalized or "0"

        return value

    @staticmethod
    def _has_value(
        value: Any,
    ) -> bool:
        """
        Determine whether a value is meaningfully populated.
        """

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

    # =========================================================
    # Minimal Result
    # =========================================================

    def _minimal_result(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Return a safe minimal company result when
        Alpha Vantage cannot provide a profile.
        """

        return {
            "symbol": symbol,
            "ticker": symbol,
            "source": self.name,
        }

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Check Alpha Vantage configuration.

        No live API request is made here because health checks
        may run frequently and should not consume API quota.
        """

        if not self.api_key:
            logger.warning(
                "Alpha Vantage provider unavailable: "
                "ALPHA_VANTAGE_API_KEY is not configured."
            )

            return False

        return True