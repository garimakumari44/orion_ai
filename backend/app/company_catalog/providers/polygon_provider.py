"""
app/company_catalog/providers/polygon_provider.py

Polygon.io Provider.

Responsibilities
----------------
- Search public companies using Polygon reference tickers.
- Retrieve detailed ticker/company profiles.
- Retrieve batches of reference tickers.
- Preserve Polygon provider metadata.
- Normalize identity metadata into the canonical company structure.
- Preserve explicit classification metadata when Polygon provides it.
- Never infer industry from sector or SIC description.

Configuration
-------------
POLYGON_API_KEY
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


class PolygonProvider(BaseProvider):
    """
    Polygon.io company-data provider.

    Polygon is used for:

        1. Company discovery.
        2. Company profile enrichment.
        3. Reference ticker synchronization.

    The provider returns provider-neutral dictionaries while
    preserving the complete Polygon response under `provider_data`.
    """

    name = "polygon"

    BASE_URL = "https://api.polygon.io"

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
        Initialize Polygon provider.

        If api_key is not supplied, POLYGON_API_KEY is read
        from the environment.
        """

        self.api_key = (
            api_key
            or os.getenv("POLYGON_API_KEY")
            or ""
        ).strip()

        self.timeout = max(
            int(timeout),
            1,
        )

    # =========================================================
    # Search Companies
    # =========================================================

    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search Polygon reference tickers.

        Polygon's reference ticker endpoint is used for discovery.

        Search results are normalized into the canonical company
        structure expected by ProviderManager.
        """

        if not isinstance(query, str):
            raise TypeError(
                "Polygon company search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        if not self.api_key:
            logger.warning(
                "Polygon API key is not configured."
            )
            return []

        try:
            response = await self._request(
                "/v3/reference/tickers",
                params={
                    "search": query,
                    "market": "stocks",
                    "active": "true",
                    "limit": 20,
                },
            )

            if not isinstance(response, dict):
                return []

            if self._is_error_response(response):
                logger.warning(
                    "Polygon search returned an error | query=%s | response=%r",
                    query,
                    response,
                )
                return []

            results = response.get(
                "results",
                [],
            )

            if not isinstance(results, list):
                return []

            companies: list[dict[str, Any]] = []

            for item in results:
                if not isinstance(item, dict):
                    continue

                company = self._normalize_ticker_record(
                    item
                )

                if company:
                    companies.append(company)

            return companies

        except Exception:
            logger.exception(
                "Polygon company search failed | query=%s",
                query,
            )

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
        Retrieve a batch of active stock tickers.

        Polygon uses cursor-based pagination. The BaseProvider
        contract uses offset-based pagination, so this method
        translates the requested offset into page traversal.

        This method is intentionally conservative because Polygon
        pagination can return large datasets.
        """

        if limit <= 0:
            return []

        if offset < 0:
            offset = 0

        if not self.api_key:
            logger.warning(
                "Polygon API key is not configured."
            )
            return []

        # Polygon's endpoint is cursor-based. We walk pages until
        # enough records have been skipped.
        remaining_skip = offset
        collected: list[dict[str, Any]] = []

        next_url: str | None = None

        try:
            while len(collected) < limit:

                if next_url:
                    response = await self._request_url(
                        next_url
                    )
                else:
                    response = await self._request(
                        "/v3/reference/tickers",
                        params={
                            "market": "stocks",
                            "active": "true",
                            "limit": min(
                                1000,
                                max(
                                    limit,
                                    100,
                                ),
                            ),
                        },
                    )

                if not isinstance(response, dict):
                    break

                if self._is_error_response(response):
                    logger.warning(
                        "Polygon list request returned an error | "
                        "response=%r",
                        response,
                    )
                    break

                results = response.get(
                    "results",
                    [],
                )

                if not isinstance(results, list):
                    break

                if not results:
                    break

                for item in results:

                    if not isinstance(item, dict):
                        continue

                    if remaining_skip > 0:
                        remaining_skip -= 1
                        continue

                    company = self._normalize_ticker_record(
                        item
                    )

                    if company:
                        collected.append(company)

                    if len(collected) >= limit:
                        break

                if len(collected) >= limit:
                    break

                next_url = response.get(
                    "next_url"
                )

                if not isinstance(next_url, str):
                    break

                next_url = next_url.strip()

                if not next_url:
                    break

                # Polygon's next_url may not contain the API key.
                if "apiKey=" not in next_url:
                    separator = (
                        "&"
                        if "?" in next_url
                        else "?"
                    )

                    next_url = (
                        f"{next_url}"
                        f"{separator}"
                        f"apiKey={self.api_key}"
                    )

            return collected[:limit]

        except Exception:
            logger.exception(
                "Polygon company listing failed | "
                "limit=%d | offset=%d",
                limit,
                offset,
            )

            return collected[:limit]

    # =========================================================
    # Company Profile
    # =========================================================

    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve detailed Polygon ticker information.

        Polygon ticker details may include:

            ticker
            name
            market
            locale
            primary_exchange
            type
            active
            currency_name
            cik
            composite_figi
            share_class_figi
            description
            homepage_url
            total_employees
            list_date
            sic_code
            sic_description
            branding
            market_cap
            phone_number
            address

        All available provider fields are preserved in
        `provider_data`.

        IMPORTANT:

        SIC information is preserved separately.

        We do NOT perform:

            industry = sic_description

        and we do NOT perform:

            industry = sector
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "Polygon company symbol must be a string."
            )

        symbol = symbol.strip().upper()

        if not symbol:
            return {}

        if not self.api_key:
            logger.warning(
                "Polygon API key is not configured."
            )

            return {
                "symbol": symbol,
                "ticker": symbol,
                "source": self.name,
            }

        try:
            response = await self._request(
                f"/v3/reference/tickers/{symbol}",
            )

            if not isinstance(response, dict):
                return {
                    "symbol": symbol,
                    "ticker": symbol,
                    "source": self.name,
                }

            if self._is_error_response(response):
                logger.warning(
                    "Polygon profile returned an error | "
                    "symbol=%s | response=%r",
                    symbol,
                    response,
                )

                return {
                    "symbol": symbol,
                    "ticker": symbol,
                    "source": self.name,
                }

            record = response.get(
                "results"
            )

            if not isinstance(record, dict):
                return {
                    "symbol": symbol,
                    "ticker": symbol,
                    "source": self.name,
                }

            result = self._normalize_ticker_record(
                record
            )

            if not result:
                return {
                    "symbol": symbol,
                    "ticker": symbol,
                    "source": self.name,
                }

            # -------------------------------------------------
            # Preserve the complete Polygon profile.
            # -------------------------------------------------

            result["provider_data"] = dict(
                record
            )

            return result

        except Exception:
            logger.exception(
                "Polygon company profile failed | symbol=%s",
                symbol,
            )

            return {
                "symbol": symbol,
                "ticker": symbol,
                "source": self.name,
            }

    # =========================================================
    # Normalize Polygon Record
    # =========================================================

    def _normalize_ticker_record(
        self,
        record: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert Polygon ticker data into canonical company data.

        Provider-specific fields are retained.
        """

        if not isinstance(record, dict):
            return {}

        ticker = self._first_value(
            record,
            "ticker",
            "symbol",
        )

        name = self._first_value(
            record,
            "name",
            "company_name",
        )

        if not ticker and not name:
            return {}

        ticker = (
            str(ticker).strip().upper()
            if self._has_value(ticker)
            else None
        )

        result: dict[str, Any] = dict(record)

        result["source"] = self.name

        # -----------------------------------------------------
        # Identity
        # -----------------------------------------------------

        self._set_if_present(
            result,
            "ticker",
            ticker,
        )

        self._set_if_present(
            result,
            "symbol",
            ticker,
        )

        self._set_if_present(
            result,
            "name",
            name,
        )

        self._set_if_present(
            result,
            "company_name",
            name,
        )

        self._set_if_present(
            result,
            "exchange",
            self._first_value(
                record,
                "primary_exchange",
                "exchange",
            ),
        )

        self._set_if_present(
            result,
            "exchange_code",
            self._first_value(
                record,
                "primary_exchange",
                "exchange",
            ),
        )

        self._set_if_present(
            result,
            "country",
            self._first_value(
                record,
                "locale",
                "country",
            ),
        )

        # -----------------------------------------------------
        # Regulatory / market identifiers
        # -----------------------------------------------------

        cik = self._first_value(
            record,
            "cik",
            "CIK",
        )

        normalized_cik = self._normalize_cik(
            cik
        )

        if normalized_cik:
            result["cik"] = normalized_cik

        self._set_if_present(
            result,
            "figi",
            self._first_value(
                record,
                "composite_figi",
                "figi",
                "FIGI",
            ),
        )

        self._set_if_present(
            result,
            "share_class_figi",
            self._first_value(
                record,
                "share_class_figi",
                "shareClassFIGI",
            ),
        )

        # -----------------------------------------------------
        # Company information
        # -----------------------------------------------------

        self._set_if_present(
            result,
            "description",
            self._first_value(
                record,
                "description",
            ),
        )

        self._set_if_present(
            result,
            "website",
            self._first_value(
                record,
                "homepage_url",
                "website",
            ),
        )

        self._set_if_present(
            result,
            "phone",
            self._first_value(
                record,
                "phone_number",
                "phone",
            ),
        )

        self._set_if_present(
            result,
            "total_employees",
            self._first_value(
                record,
                "total_employees",
            ),
        )

        self._set_if_present(
            result,
            "list_date",
            self._first_value(
                record,
                "list_date",
            ),
        )

        self._set_if_present(
            result,
            "market",
            self._first_value(
                record,
                "market",
            ),
        )

        self._set_if_present(
            result,
            "locale",
            self._first_value(
                record,
                "locale",
            ),
        )

        self._set_if_present(
            result,
            "asset_type",
            self._first_value(
                record,
                "type",
            ),
        )

        self._set_if_present(
            result,
            "currency",
            self._first_value(
                record,
                "currency_name",
                "currency",
            ),
        )

        self._set_if_present(
            result,
            "market_cap",
            self._first_value(
                record,
                "market_cap",
            ),
        )

        # -----------------------------------------------------
        # Address
        # -----------------------------------------------------

        address = record.get(
            "address"
        )

        if isinstance(address, dict):
            result["address"] = dict(
                address
            )

        # -----------------------------------------------------
        # SIC classification
        # -----------------------------------------------------
        #
        # Preserve explicitly.
        #
        # DO NOT map:
        #
        #     sic_description -> industry
        #
        # because the current architecture requires explicit
        # industry metadata.
        # -----------------------------------------------------

        self._set_if_present(
            result,
            "sic_code",
            self._first_value(
                record,
                "sic_code",
                "sic",
            ),
        )

        self._set_if_present(
            result,
            "sic_description",
            self._first_value(
                record,
                "sic_description",
            ),
        )

        # -----------------------------------------------------
        # Branding
        # -----------------------------------------------------

        branding = record.get(
            "branding"
        )

        if isinstance(branding, dict):
            branding_copy = dict(
                branding
            )

            result["branding"] = branding_copy

            self._set_if_present(
                result,
                "logo_url",
                self._first_value(
                    branding,
                    "logo_url",
                    "logoUrl",
                ),
            )

            self._set_if_present(
                result,
                "icon_url",
                self._first_value(
                    branding,
                    "icon_url",
                    "iconUrl",
                ),
            )

        # -----------------------------------------------------
        # Preserve provider payload.
        # -----------------------------------------------------

        result["provider_data"] = dict(
            record
        )

        return result

    # =========================================================
    # HTTP
    # =========================================================

    async def _request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Perform an asynchronous Polygon API request.
        """

        if not path.startswith("http"):
            url = (
                f"{self.BASE_URL}"
                f"{path}"
            )
        else:
            url = path

        request_params = dict(
            params or {}
        )

        request_params.setdefault(
            "apiKey",
            self.api_key,
        )

        url = (
            f"{url}?"
            f"{urlencode(request_params)}"
        )

        return await self._request_url(
            url
        )

    async def _request_url(
        self,
        url: str,
    ) -> dict[str, Any]:
        """
        Execute a URL request in a worker thread.
        """

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
        Synchronous JSON request used by asyncio.to_thread().
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
    # Error Handling
    # =========================================================

    @staticmethod
    def _is_error_response(
        response: dict[str, Any],
    ) -> bool:
        """
        Detect common Polygon API error responses.
        """

        if response.get("error"):
            return True

        status = response.get(
            "status"
        )

        if isinstance(status, str):
            if status.lower() in {
                "error",
                "failed",
            }:
                return True

        if response.get("status_code"):
            try:
                status_code = int(
                    response["status_code"]
                )

                if status_code >= 400:
                    return True

            except (
                TypeError,
                ValueError,
            ):
                pass

        return False

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def _first_value(
        data: dict[str, Any] | None,
        *fields: str,
    ) -> Any:
        """
        Return the first meaningful field value.
        """

        if not isinstance(data, dict):
            return None

        for field in fields:
            value = data.get(
                field
            )

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
        Set a field only when populated.
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
        Normalize CIK while preserving identity.
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
        Determine whether a value is meaningful.
        """

        if value is None:
            return False

        if isinstance(value, str):
            return bool(
                value.strip()
            )

        return True

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Check provider configuration without consuming
        Polygon API quota.

        Actual API failures are handled by search/profile
        methods.
        """

        if not self.api_key:
            logger.warning(
                "Polygon provider unavailable: "
                "POLYGON_API_KEY is not configured."
            )

            return False

        return True