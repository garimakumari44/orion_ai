
"""
app/company_catalog/providers/openfigi_provider.py

OpenFIGI Provider.

Responsibilities
----------------
- Resolve securities through OpenFIGI.
- Preserve FIGI identifiers.
- Preserve ISIN/CUSIP identifiers when supplied.
- Preserve ticker and exchange metadata.
- Preserve explicit OpenFIGI classification metadata.
- Return provider-neutral dictionaries.

Architectural rules
-------------------
- OpenFIGI is primarily an identifier-mapping provider.
- This provider does NOT infer canonical industry.
- market_sector is never converted into industry.
- API credentials are configuration-ready but are not required
  until the application's provider configuration layer exists.
"""

from __future__ import annotations

from typing import Any

import httpx

from .base import BaseProvider


class OpenFIGIProvider(BaseProvider):
    """
    OpenFIGI security/company identifier provider.

    OpenFIGI is used primarily to enrich company records with
    market-security identifiers and exchange metadata.
    """

    name = "openfigi"

    BASE_URL = "https://api.openfigi.com/v3"

    MAPPING_URL = f"{BASE_URL}/mapping"

    REQUEST_TIMEOUT = 10.0

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize OpenFIGI provider.

        API-key handling is intentionally dependency-free for now.
        The key can later be supplied by the application's
        configuration/settings layer.
        """

        self.api_key = (
            api_key.strip()
            if isinstance(api_key, str) and api_key.strip()
            else None
        )

    # =========================================================
    # Search Companies
    # =========================================================

    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search OpenFIGI using a ticker/security query.

        OpenFIGI is not a general company search engine, so this
        method is intentionally conservative.

        The query is treated primarily as a ticker/security symbol.
        """

        if not isinstance(query, str):
            raise TypeError(
                "OpenFIGI search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        # OpenFIGI mapping requires a structured mapping request.
        # We currently support ticker-style discovery.
        request = {
            "ticker": query.upper(),
        }

        results = await self._mapping_request(
            request,
        )

        return self._normalize_results(results)

    # =========================================================
    # List Companies
    # =========================================================

    async def list_companies(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        OpenFIGI does not expose a complete company catalog.

        Bulk catalog synchronization therefore remains unsupported.
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
        Resolve a security/company identifier through OpenFIGI.

        The returned record contains all meaningful metadata that
        OpenFIGI explicitly provides.

        No industry inference is performed.
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "OpenFIGI symbol must be a string."
            )

        symbol = symbol.strip()

        if not symbol:
            return {}

        results = await self._mapping_request(
            {
                "ticker": symbol.upper(),
            },
        )

        normalized = self._normalize_results(
            results,
        )

        if not normalized:
            return {
                "symbol": symbol.upper(),
                "ticker": symbol.upper(),
                "source": self.name,
            }

        # Return the strongest mapping result.
        result = normalized[0]

        result.setdefault(
            "symbol",
            symbol.upper(),
        )

        result["source"] = self.name

        return result

    # =========================================================
    # Mapping API
    # =========================================================

    async def _mapping_request(
        self,
        mapping: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Execute an OpenFIGI mapping request.

        OpenFIGI accepts POST requests containing mapping objects.

        API credentials are optional for the moment because the
        project's centralized provider configuration layer has not
        yet been implemented.
        """

        if not isinstance(mapping, dict):
            return []

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["X-OPENFIGI-APIKEY"] = self.api_key

        payload = [mapping]

        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                headers=headers,
            ) as client:

                response = await client.post(
                    self.MAPPING_URL,
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

        except Exception:
            return []

        if not isinstance(data, list):
            return []

        results: list[dict[str, Any]] = []

        for item in data:

            if not isinstance(item, dict):
                continue

            # OpenFIGI normally returns:
            #
            # {
            #     "data": [...]
            # }
            #
            # or an error object.

            mapped_data = item.get("data")

            if isinstance(mapped_data, list):

                for record in mapped_data:

                    if isinstance(record, dict):
                        results.append(record)

        return results

    # =========================================================
    # Normalize Results
    # =========================================================

    def _normalize_results(
        self,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Convert OpenFIGI responses into provider-neutral records.

        All meaningful OpenFIGI metadata is preserved.

        Classification metadata is only retained when explicitly
        supplied by OpenFIGI.
        """

        normalized: list[dict[str, Any]] = []

        for raw in results:

            if not isinstance(raw, dict):
                continue

            record: dict[str, Any] = {
                "source": self.name,
            }

            # -------------------------------------------------
            # Identity
            # -------------------------------------------------

            self._copy_if_present(
                record,
                "name",
                raw.get("name"),
            )

            self._copy_if_present(
                record,
                "ticker",
                raw.get("ticker"),
            )

            self._copy_if_present(
                record,
                "exchange",
                raw.get("exchCode"),
            )

            self._copy_if_present(
                record,
                "exchange_code",
                raw.get("exchCode"),
            )

            # -------------------------------------------------
            # FIGI identifiers
            # -------------------------------------------------

            self._copy_if_present(
                record,
                "figi",
                raw.get("figi"),
            )

            self._copy_if_present(
                record,
                "composite_figi",
                raw.get("compositeFIGI"),
            )

            self._copy_if_present(
                record,
                "share_class_figi",
                raw.get("shareClassFIGI"),
            )

            # -------------------------------------------------
            # Security identifiers
            # -------------------------------------------------

            self._copy_if_present(
                record,
                "isin",
                raw.get("isin"),
            )

            self._copy_if_present(
                record,
                "cusip",
                raw.get("cusip"),
            )

            self._copy_if_present(
                record,
                "sedol",
                raw.get("sedol"),
            )

            # -------------------------------------------------
            # Security metadata
            # -------------------------------------------------

            self._copy_if_present(
                record,
                "security_type",
                raw.get("securityType"),
            )

            self._copy_if_present(
                record,
                "security_type2",
                raw.get("securityType2"),
            )

            self._copy_if_present(
                record,
                "security_description",
                raw.get("securityDescription"),
            )

            self._copy_if_present(
                record,
                "market_sector",
                raw.get("marketSector"),
            )

            self._copy_if_present(
                record,
                "market_sector_description",
                raw.get("marketSectorDescription"),
            )

            # -------------------------------------------------
            # Classification
            #
            # IMPORTANT:
            #
            # marketSector is NOT mapped to canonical sector
            # or industry.
            # -------------------------------------------------

            self._copy_if_present(
                record,
                "industry",
                raw.get("industry"),
            )

            self._copy_if_present(
                record,
                "sector",
                raw.get("sector"),
            )

            self._copy_if_present(
                record,
                "sub_industry",
                raw.get("subIndustry"),
            )

            # -------------------------------------------------
            # Preserve additional OpenFIGI metadata
            # -------------------------------------------------

            known_fields = {
                "name",
                "ticker",
                "exchCode",
                "figi",
                "compositeFIGI",
                "shareClassFIGI",
                "isin",
                "cusip",
                "sedol",
                "securityType",
                "securityType2",
                "securityDescription",
                "marketSector",
                "marketSectorDescription",
                "industry",
                "sector",
                "subIndustry",
            }

            metadata: dict[str, Any] = {}

            for key, value in raw.items():

                if key in known_fields:
                    continue

                if self._has_value(value):
                    metadata[key] = value

            if metadata:
                record["provider_metadata"] = metadata

            normalized.append(record)

        return normalized

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify that OpenFIGI is reachable.

        A failed health check does not crash the application.
        """

        headers: dict[str, str] = {}

        if self.api_key:
            headers["X-OPENFIGI-APIKEY"] = self.api_key

        try:
            async with httpx.AsyncClient(
                timeout=5.0,
                headers=headers,
            ) as client:

                response = await client.get(
                    self.BASE_URL,
                )

                return response.status_code < 500

        except Exception:
            return False

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def _copy_if_present(
        target: dict[str, Any],
        field: str,
        value: Any,
    ) -> None:
        """
        Copy a meaningful value into the target dictionary.
        """

        if value is None:
            return

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return

        target[field] = value

    @staticmethod
    def _has_value(
        value: Any,
    ) -> bool:
        """
        Return True when a value is meaningfully populated.
        """

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

