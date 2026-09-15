
"""
app/company_catalog/providers/yahoo_provider.py

Yahoo Finance Provider.

Responsibilities
----------------
- Search companies using Yahoo Finance.
- Retrieve detailed company profiles.
- Preserve canonical classification metadata.
- Return provider-neutral dictionaries.

Canonical classification fields
--------------------------------
sector
industry
sub_industry

Important
---------
sector != industry != sub_industry

This provider never uses sector as industry.
"""

from __future__ import annotations

from typing import Any

from yahooquery import Ticker, search

from .base import BaseProvider


class YahooProvider(BaseProvider):
    """
    Yahoo Finance company-data provider.

    Yahoo is primarily used for:

        1. Company discovery.
        2. Company profile enrichment.

    Search results may contain only basic identity information.
    Detailed profile lookup is used to obtain additional metadata
    when available.
    """

    name = "yahoo"

    # =========================================================
    # Search Companies
    # =========================================================

    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search Yahoo Finance for companies.

        Search is a discovery operation. The returned records may
        not contain complete industry classification.

        Detailed classification should be obtained through
        get_company_profile() when a company becomes research-ready.
        """

        if not isinstance(query, str):
            raise TypeError(
                "Yahoo company search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        try:
            response = search(query)

            if not isinstance(response, dict):
                return []

            quotes = response.get("quotes", [])

            if not isinstance(quotes, list):
                return []

            companies: list[dict[str, Any]] = []

            for item in quotes:
                if not isinstance(item, dict):
                    continue

                # -------------------------------------------------
                # Only equities
                # -------------------------------------------------

                if item.get("quoteType") != "EQUITY":
                    continue

                name = (
                    item.get("longname")
                    or item.get("shortname")
                )

                ticker = item.get("symbol")

                if not name or not ticker:
                    continue

                company: dict[str, Any] = {
                    "name": str(name).strip(),
                    "ticker": str(ticker).strip().upper(),
                    "exchange": self._first_value(
                        item,
                        "exchange",
                        "exchangeCode",
                    ),
                    "country": self._first_value(
                        item,
                        "country",
                        "countryName",
                    ),
                    "website": None,
                    "logo_url": None,
                    "source": self.name,
                }

                # -------------------------------------------------
                # Preserve classification if Yahoo search happens
                # to provide it.
                #
                # We NEVER infer industry from sector.
                # -------------------------------------------------

                sector = self._first_value(
                    item,
                    "sector",
                    "sector_name",
                    "sectorName",
                )

                industry = self._first_value(
                    item,
                    "industry",
                    "industry_name",
                    "industryName",
                    "industry_classification",
                )

                sub_industry = self._first_value(
                    item,
                    "sub_industry",
                    "subindustry",
                    "subIndustry",
                    "sub_industry_name",
                    "subIndustryName",
                    "industry_group",
                    "industryGroup",
                )

                if sector:
                    company["sector"] = sector

                if industry:
                    company["industry"] = industry

                if sub_industry:
                    company["sub_industry"] = sub_industry

                companies.append(company)

            return companies

        except Exception:
            # Provider failures must not crash the company
            # catalog pipeline.
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
        Yahoo Finance does not expose a reliable complete company
        catalog through this provider.

        A maintained exchange-symbol universe should eventually
        be combined with Yahoo profile enrichment for bulk catalog
        synchronization.
        """

        if limit <= 0:
            return []

        if offset < 0:
            offset = 0

        return []

    # =========================================================
    # Company Profile
    # =========================================================

    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve a detailed Yahoo Finance company profile.

        The profile attempts to provide:

            name
            ticker
            exchange
            country
            website
            description
            sector
            industry

        Yahoo does not expose a guaranteed universal sub-industry
        classification. Therefore sub_industry is only populated
        when Yahoo explicitly provides an appropriate field.

        The method never derives:

            industry = sector

        """

        if not isinstance(symbol, str):
            raise TypeError(
                "Yahoo company symbol must be a string."
            )

        symbol = symbol.strip().upper()

        if not symbol:
            return {}

        try:
            ticker = Ticker(symbol)

            # -----------------------------------------------------
            # summaryProfile is the primary Yahoo profile source.
            # yahooquery may return either a dictionary keyed by
            # symbol or an error/empty value.
            # -----------------------------------------------------

            profile_data = await self._get_summary_profile(
                ticker
            )

            # -----------------------------------------------------
            # Quote type / price information can provide additional
            # identity metadata.
            # -----------------------------------------------------

            price_data = await self._get_price_data(
                ticker
            )

            profile = self._extract_symbol_record(
                profile_data,
                symbol,
            )

            price = self._extract_symbol_record(
                price_data,
                symbol,
            )

            result: dict[str, Any] = {
                "symbol": symbol,
                "ticker": symbol,
                "source": self.name,
            }

            # -----------------------------------------------------
            # Identity
            # -----------------------------------------------------

            self._copy_if_present(
                result,
                "name",
                self._first_value(
                    profile,
                    "longName",
                    "shortName",
                    "displayName",
                    "name",
                )
                or self._first_value(
                    price,
                    "longName",
                    "shortName",
                    "displayName",
                    "name",
                ),
            )

            self._copy_if_present(
                result,
                "exchange",
                self._first_value(
                    price,
                    "exchange",
                    "exchangeName",
                    "fullExchangeName",
                )
                or self._first_value(
                    profile,
                    "exchange",
                    "exchangeName",
                    "fullExchangeName",
                ),
            )

            # -----------------------------------------------------
            # Company information
            # -----------------------------------------------------

            self._copy_if_present(
                result,
                "country",
                self._first_value(
                    profile,
                    "country",
                    "countryName",
                ),
            )

            self._copy_if_present(
                result,
                "website",
                self._first_value(
                    profile,
                    "website",
                    "websiteUrl",
                ),
            )

            self._copy_if_present(
                result,
                "description",
                self._first_value(
                    profile,
                    "longBusinessSummary",
                    "description",
                    "businessSummary",
                ),
            )

            # -----------------------------------------------------
            # Canonical classification
            # -----------------------------------------------------

            sector = self._first_value(
                profile,
                "sector",
                "sector_name",
                "sectorName",
            )

            industry = self._first_value(
                profile,
                "industry",
                "industry_name",
                "industryName",
                "industry_classification",
            )

            sub_industry = self._first_value(
                profile,
                "sub_industry",
                "subindustry",
                "subIndustry",
                "sub_industry_name",
                "subIndustryName",
                "industry_group",
                "industryGroup",
            )

            if sector:
                result["sector"] = sector

            if industry:
                result["industry"] = industry

            if sub_industry:
                result["sub_industry"] = sub_industry

            return result

        except Exception:
            return {
                "symbol": symbol,
                "ticker": symbol,
                "source": self.name,
            }

    # =========================================================
    # Yahoo Data Helpers
    # =========================================================

    async def _get_summary_profile(
        self,
        ticker: Ticker,
    ) -> Any:
        """
        Safely retrieve Yahoo summary profile data.

        yahooquery generally exposes summary_profile as a property,
        but versions/providers may differ in how the result is
        represented. This helper keeps that detail isolated.
        """

        try:
            value = ticker.summary_profile

            if hasattr(value, "__await__"):
                value = await value

            return value

        except Exception:
            return {}

    async def _get_price_data(
        self,
        ticker: Ticker,
    ) -> Any:
        """
        Safely retrieve Yahoo price metadata.
        """

        try:
            value = ticker.price

            if hasattr(value, "__await__"):
                value = await value

            return value

        except Exception:
            return {}

    @staticmethod
    def _extract_symbol_record(
        data: Any,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Extract a single symbol record from Yahoo response data.

        Handles common yahooquery response forms:

            {
                "AAPL": {...}
            }

        and direct dictionaries:

            {
                "sector": "...",
                "industry": "..."
            }
        """

        if not isinstance(data, dict):
            return {}

        # ---------------------------------------------------------
        # Symbol-keyed response
        # ---------------------------------------------------------

        record = data.get(symbol)

        if isinstance(record, dict):
            return record

        # Yahoo may normalize symbols differently.
        for key, value in data.items():
            if (
                isinstance(key, str)
                and key.upper() == symbol.upper()
                and isinstance(value, dict)
            ):
                return value

        # ---------------------------------------------------------
        # Direct record
        # ---------------------------------------------------------

        if any(
            field in data
            for field in (
                "sector",
                "industry",
                "longBusinessSummary",
                "website",
                "country",
            )
        ):
            return data

        return {}

    # =========================================================
    # Generic Helpers
    # =========================================================

    @staticmethod
    def _first_value(
        data: dict[str, Any] | None,
        *fields: str,
    ) -> Any:
        """
        Return the first meaningful value from a dictionary.
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
    def _copy_if_present(
        target: dict[str, Any],
        field: str,
        value: Any,
    ) -> None:
        """
        Add a field only when a meaningful value exists.
        """

        if value is None:
            return

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return

        target[field] = value

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Yahoo provider availability check.

        The provider itself does not require a persistent
        connection, so this is currently a lightweight check.
        """

        return True

