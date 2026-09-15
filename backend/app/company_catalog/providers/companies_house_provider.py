
"""
app/company_catalog/providers/companies_house_provider.py

UK Companies House Provider.

Responsibilities
----------------
- Search UK companies using Companies House.
- Retrieve detailed company profiles.
- Preserve registration metadata.
- Preserve SIC codes separately.
- Preserve explicit classification metadata when available.
- Return provider-neutral dictionaries.

Architectural rules
-------------------
- No database access.
- No LLM calls.
- No investment analysis.
- No industry inference from SIC codes.
- API credentials are injected into the provider.
- Provider failures return safe empty results.

Canonical classification
------------------------
sector
industry
sub_industry

Companies House primarily exposes SIC information.
Therefore:

    sic_codes != industry
    sic_description != industry

SIC metadata is preserved as:

    sic_codes
    sic_description
"""

from __future__ import annotations

from typing import Any

import httpx

from .base import BaseProvider


class CompaniesHouseProvider(BaseProvider):
    """
    Companies House company-data provider.

    Companies House identifies companies primarily by
    company number rather than stock ticker.

    The provider supports:

        1. Company name search.
        2. Company profile lookup.
        3. Basic API health checking.

    Bulk catalog synchronization is intentionally not
    implemented because Companies House does not expose
    a simple complete-company catalog endpoint suitable
    for this provider abstraction.
    """

    name = "companies_house"

    BASE_URL = "https://api.company-information.service.gov.uk"

    SEARCH_URL = (
        f"{BASE_URL}/search/companies"
    )

    REQUEST_TIMEOUT = 10.0

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize the Companies House provider.

        Parameters
        ----------
        api_key:
            Companies House API key.

        The key is injected by the application layer rather
        than hardcoded inside the provider.
        """

        self.api_key = (
            api_key.strip()
            if isinstance(api_key, str)
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
        Search Companies House by company name.

        Companies House search results primarily contain
        company identity and registration metadata.

        No industry is inferred from SIC information.
        """

        if not isinstance(query, str):
            raise TypeError(
                "Companies House search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        if not self.api_key:
            return []

        params = {
            "q": query,
        }

        try:
            response = await self._request(
                "GET",
                self.SEARCH_URL,
                params=params,
            )

            if not isinstance(response, dict):
                return []

            items = response.get(
                "items",
                [],
            )

            if not isinstance(items, list):
                return []

            companies: list[dict[str, Any]] = []

            for item in items:
                if not isinstance(item, dict):
                    continue

                company = self._normalize_search_result(
                    item
                )

                if company:
                    companies.append(company)

            return companies

        except Exception:
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
        Return a batch of companies.

        Companies House does not expose a simple complete
        company-catalog endpoint appropriate for this provider.

        Bulk ingestion should eventually use a dedicated
        Companies House bulk-data ingestion workflow rather
        than pretending the search endpoint is a catalog.

        Therefore this method intentionally returns [].
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
        Retrieve a detailed Companies House company profile.

        ``symbol`` is expected to be a Companies House
        company number.

        Example:

            01234567

        The returned dictionary is provider-neutral.
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "Companies House company number must be a string."
            )

        company_number = symbol.strip().upper()

        if not company_number:
            return {}

        if not self.api_key:
            return {}

        url = (
            f"{self.BASE_URL}/company/"
            f"{company_number}"
        )

        try:
            payload = await self._request(
                "GET",
                url,
            )

            if not isinstance(payload, dict):
                return {}

            return self._normalize_profile(
                payload
            )

        except Exception:
            return {}

    # =========================================================
    # HTTP Request
    # =========================================================

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute an authenticated Companies House request.

        Companies House uses HTTP Basic Authentication
        with the API key as the username and an empty
        password.
        """

        if not self.api_key:
            raise RuntimeError(
                "Companies House API key is not configured."
            )

        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "EnterpriseResearchCompanyCatalog"
            ),
        }

        auth = (
            self.api_key,
            "",
        )

        async with httpx.AsyncClient(
            timeout=self.REQUEST_TIMEOUT,
            headers=headers,
            auth=auth,
        ) as client:

            response = await client.request(
                method,
                url,
                params=params,
            )

            response.raise_for_status()

            return response.json()

    # =========================================================
    # Search Result Normalization
    # =========================================================

    @classmethod
    def _normalize_search_result(
        cls,
        item: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Convert a Companies House search result into the
        canonical provider-neutral company dictionary.
        """

        company_number = cls._first_value(
            item,
            "company_number",
        )

        name = cls._first_value(
            item,
            "title",
            "company_name",
        )

        if not company_number and not name:
            return None

        result: dict[str, Any] = {
            "name": name,
            "company_number": company_number,
            "company_status": cls._first_value(
                item,
                "company_status",
            ),
            "company_type": cls._first_value(
                item,
                "company_type",
            ),
            "date_of_cessation": cls._first_value(
                item,
                "date_of_cessation",
            ),
            "date_of_creation": cls._first_value(
                item,
                "date_of_creation",
            ),
            "registered_office": cls._normalize_address(
                item.get("address")
            ),
            "source": cls.name,
        }

        # -----------------------------------------------------
        # Preserve explicit classification if present.
        #
        # SIC is NOT converted into industry.
        # -----------------------------------------------------

        sic_codes = cls._normalize_sic_codes(
            item.get("sic_codes")
        )

        if sic_codes:
            result["sic_codes"] = sic_codes

        cls._copy_if_present(
            result,
            "industry",
            item.get("industry"),
        )

        cls._copy_if_present(
            result,
            "sub_industry",
            item.get("sub_industry"),
        )

        cls._copy_if_present(
            result,
            "sector",
            item.get("sector"),
        )

        return cls._remove_empty_values(
            result
        )

    # =========================================================
    # Profile Normalization
    # =========================================================

    @classmethod
    def _normalize_profile(
        cls,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize the Companies House company profile.

        All useful provider metadata is preserved where
        practical while canonical fields are populated.
        """

        address = payload.get(
            "registered_office_address"
        )

        result: dict[str, Any] = {
            "name": cls._first_value(
                payload,
                "company_name",
                "name",
            ),
            "company_number": cls._first_value(
                payload,
                "company_number",
            ),
            "company_status": cls._first_value(
                payload,
                "company_status",
            ),
            "company_status_detail": cls._first_value(
                payload,
                "company_status_detail",
            ),
            "company_type": cls._first_value(
                payload,
                "type",
                "company_type",
            ),
            "date_of_creation": cls._first_value(
                payload,
                "date_of_creation",
            ),
            "date_of_cessation": cls._first_value(
                payload,
                "date_of_cessation",
            ),
            "etag": cls._first_value(
                payload,
                "etag",
            ),
            "jurisdiction": cls._first_value(
                payload,
                "jurisdiction",
            ),
            "registered_office": cls._normalize_address(
                address
            ),
            "sic_codes": cls._normalize_sic_codes(
                payload.get("sic_codes")
            ),
            "undeliverable_registered_office": payload.get(
                "undeliverable_registered_office"
            ),
            "has_insolvency_history": payload.get(
                "has_insolvency_history"
            ),
            "has_charges": payload.get(
                "has_charges"
            ),
            "has_super_secure_pscs": payload.get(
                "has_super_secure_pscs"
            ),
            "can_file": payload.get(
                "can_file"
            ),
            "accounts_next_due": cls._first_value(
                payload,
                "accounts",
                "accounts_next_due",
            ),
            "confirmation_statement_next_due": cls._first_value(
                payload,
                "confirmation_statement",
                "confirmation_statement_next_due",
            ),
            "source": cls.name,
        }

        # -----------------------------------------------------
        # URI/reference metadata
        # -----------------------------------------------------

        links = payload.get(
            "links"
        )

        if isinstance(links, dict):
            cls._copy_if_present(
                result,
                "self_url",
                links.get("self"),
            )

            cls._copy_if_present(
                result,
                "filing_history_url",
                links.get("filing_history"),
            )

            cls._copy_if_present(
                result,
                "officers_url",
                links.get("officers"),
            )

            cls._copy_if_present(
                result,
                "persons_with_significant_control_url",
                links.get(
                    "persons_with_significant_control"
                ),
            )

        # -----------------------------------------------------
        # SIC descriptions
        # -----------------------------------------------------
        #
        # Companies House commonly provides SIC codes but
        # does not provide a canonical industry field.
        #
        # We preserve the codes without converting them.
        # -----------------------------------------------------

        sic_description = payload.get(
            "sic_description"
        )

        if cls._has_value(
            sic_description
        ):
            result["sic_description"] = (
                str(sic_description).strip()
            )

        # -----------------------------------------------------
        # Explicit classification only
        # -----------------------------------------------------

        for field in (
            "sector",
            "industry",
            "sub_industry",
        ):
            cls._copy_if_present(
                result,
                field,
                payload.get(field),
            )

        # -----------------------------------------------------
        # Preserve other useful company metadata
        # -----------------------------------------------------

        cls._copy_if_present(
            result,
            "previous_company_names",
            payload.get(
                "previous_company_names"
            ),
        )

        cls._copy_if_present(
            result,
            "accounting_reference_date",
            payload.get(
                "accounts",
                {},
            ).get(
                "accounting_reference_date"
            )
            if isinstance(
                payload.get("accounts"),
                dict,
            )
            else None,
        )

        cls._copy_if_present(
            result,
            "confirmation_statement",
            payload.get(
                "confirmation_statement"
            ),
        )

        return cls._remove_empty_values(
            result
        )

    # =========================================================
    # Address
    # =========================================================

    @classmethod
    def _normalize_address(
        cls,
        address: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize a Companies House address object.

        The address remains structured rather than being
        flattened into a single string.
        """

        if not isinstance(address, dict):
            return None

        normalized: dict[str, Any] = {}

        fields = (
            "premises",
            "address_line_1",
            "address_line_2",
            "locality",
            "region",
            "postal_code",
            "country",
            "care_of",
            "po_box",
        )

        for field in fields:
            value = address.get(field)

            if cls._has_value(value):
                normalized[field] = (
                    str(value).strip()
                    if isinstance(value, str)
                    else value
                )

        return normalized or None

    # =========================================================
    # SIC
    # =========================================================

    @staticmethod
    def _normalize_sic_codes(
        value: Any,
    ) -> list[str]:
        """
        Normalize Companies House SIC codes.

        SIC codes are identifiers/classification metadata.
        They are deliberately kept separate from canonical
        ``industry``.
        """

        if not isinstance(value, (list, tuple)):
            return []

        result: list[str] = []

        for code in value:
            if code is None:
                continue

            normalized = str(code).strip()

            if not normalized:
                continue

            if normalized not in result:
                result.append(normalized)

        return result

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify Companies House API availability.

        When no API key is configured, the provider is
        considered unavailable.
        """

        if not self.api_key:
            return False

        try:
            response = await self._request(
                "GET",
                self.SEARCH_URL,
                params={
                    "q": "OpenAI",
                    "items_per_page": 1,
                },
            )

            return isinstance(
                response,
                dict,
            )

        except Exception:
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
    def _has_value(
        value: Any,
    ) -> bool:
        """
        Return True when a value is meaningfully populated.

        Numeric zero and False are considered valid values.
        """

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

    @classmethod
    def _copy_if_present(
        cls,
        target: dict[str, Any],
        field: str,
        value: Any,
    ) -> None:
        """
        Copy a field only when it contains useful data.
        """

        if not cls._has_value(value):
            return

        target[field] = value

    @classmethod
    def _remove_empty_values(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Remove None and empty string values.

        Empty lists/dictionaries are also removed.
        False and zero are retained.
        """

        cleaned: dict[str, Any] = {}

        for key, value in data.items():

            if value is None:
                continue

            if isinstance(value, str):
                if not value.strip():
                    continue

            elif isinstance(value, (list, dict)):
                if not value:
                    continue

            cleaned[key] = value

        return cleaned
