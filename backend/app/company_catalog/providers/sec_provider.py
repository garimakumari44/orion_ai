from __future__ import annotations

from typing import Any

import httpx

from .base import BaseProvider


class SECProvider(BaseProvider):
    """
    SEC EDGAR company-data provider.

    Responsibilities
    ----------------
    - Search SEC company/ticker data.
    - Retrieve SEC company identity metadata.
    - Preserve CIK and ticker information.
    - Preserve SEC SIC metadata when available.
    - Never infer canonical industry from SIC.

    Canonical classification rules
    ------------------------------
    sector != industry != sub_industry

    SEC SIC is preserved as ``sic_code`` and is never
    automatically converted into ``industry``.
    """

    name = "sec"

    BASE_URL = "https://www.sec.gov"

    COMPANY_TICKERS_URL = (
        f"{BASE_URL}/files/company_tickers.json"
    )

    REQUEST_TIMEOUT = 10.0

    # SEC requires a descriptive User-Agent.
    USER_AGENT = (
        "EnterpriseResearchCompanyCatalog "
        "(contact@example.com)"
    )

    def __init__(self) -> None:
        self._company_cache: list[dict[str, Any]] | None = None

    # =========================================================
    # Search Companies
    # =========================================================

    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search the SEC company ticker dataset.

        Matching is performed against:

            company name
            ticker
            CIK

        SEC search results primarily provide identity metadata.
        They do not automatically provide canonical industry.
        """

        if not isinstance(query, str):
            raise TypeError(
                "SEC company search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        companies = await self._load_company_tickers()

        if not companies:
            return []

        normalized_query = query.lower()

        results: list[dict[str, Any]] = []

        for company in companies:
            name = str(
                company.get("name") or ""
            ).lower()

            ticker = str(
                company.get("ticker") or ""
            ).lower()

            cik = str(
                company.get("cik") or ""
            ).lower()

            if (
                normalized_query in name
                or normalized_query == ticker
                or normalized_query == cik
            ):
                results.append(
                    dict(company)
                )

        return results

    # =========================================================
    # List Companies
    # =========================================================

    async def list_companies(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Return a paginated batch of SEC companies.
        """

        if limit <= 0:
            return []

        if offset < 0:
            offset = 0

        companies = await self._load_company_tickers()

        if not companies:
            return []

        return companies[
            offset : offset + limit
        ]

    # =========================================================
    # Company Profile
    # =========================================================

    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve SEC company profile metadata.

        ``symbol`` may be either:

            ticker
            CIK

        The SEC submissions endpoint is used to retrieve
        additional company metadata.

        SIC is preserved as ``sic_code`` and is NOT converted
        into canonical ``industry``.
        """

        if not isinstance(symbol, str):
            raise TypeError(
                "SEC company symbol must be a string."
            )

        symbol = symbol.strip()

        if not symbol:
            return {}

        companies = await self._load_company_tickers()

        if not companies:
            return {}

        normalized_symbol = symbol.lower()

        matched: dict[str, Any] | None = None

        for company in companies:
            ticker = str(
                company.get("ticker") or ""
            ).lower()

            cik = str(
                company.get("cik") or ""
            ).lower()

            if (
                normalized_symbol == ticker
                or normalized_symbol == cik
            ):
                matched = company
                break

        if not matched:
            return {}

        cik = str(
            matched.get("cik") or ""
        ).strip()

        result: dict[str, Any] = {
            "name": matched.get("name"),
            "ticker": matched.get("ticker"),
            "cik": cik,
            "exchange": matched.get("exchange"),
            "source": self.name,
        }

        # -----------------------------------------------------
        # Fetch SEC submissions
        # -----------------------------------------------------

        if cik:
            submissions = await self._get_submissions(
                cik
            )

            if submissions:
                self._extract_submission_metadata(
                    result,
                    submissions,
                )

        return {
            key: value
            for key, value in result.items()
            if self._has_value(value)
        }

    # =========================================================
    # SEC Company Ticker Dataset
    # =========================================================

    async def _load_company_tickers(
        self,
    ) -> list[dict[str, Any]]:
        """
        Load and normalize SEC company_tickers.json.

        Results are cached for the lifetime of the provider
        instance.
        """

        if self._company_cache is not None:
            return self._company_cache

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                headers=headers,
            ) as client:

                response = await client.get(
                    self.COMPANY_TICKERS_URL
                )

                response.raise_for_status()

                payload = response.json()

        except Exception:
            return []

        if not isinstance(payload, dict):
            return []

        normalized: list[dict[str, Any]] = []

        for item in payload.values():

            if not isinstance(item, dict):
                continue

            cik = item.get("cik_str")
            ticker = item.get("ticker")
            title = item.get("title")

            if cik is None or not ticker or not title:
                continue

            normalized.append(
                {
                    "name": str(title).strip(),
                    "ticker": str(ticker).strip().upper(),
                    "cik": self._normalize_cik(cik),
                    "source": self.name,
                }
            )

        self._company_cache = normalized

        return normalized

    # =========================================================
    # SEC Submissions
    # =========================================================

    async def _get_submissions(
        self,
        cik: str,
    ) -> dict[str, Any]:
        """
        Fetch SEC submissions metadata.
        """

        normalized_cik = self._normalize_cik(cik)

        if not normalized_cik:
            return {}

        url = (
            f"{self.BASE_URL}/submissions/"
            f"CIK{normalized_cik.zfill(10)}.json"
        )

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                headers=headers,
            ) as client:

                response = await client.get(
                    url
                )

                response.raise_for_status()

                payload = response.json()

        except Exception:
            return {}

        return (
            payload
            if isinstance(payload, dict)
            else {}
        )

    # =========================================================
    # Submission Metadata
    # =========================================================

    @staticmethod
    def _extract_submission_metadata(
        result: dict[str, Any],
        submissions: dict[str, Any],
    ) -> None:
        """
        Extract explicit SEC metadata.

        Important:
        SIC is preserved separately. It is never converted
        into canonical industry.
        """

        sic = submissions.get("sic")

        if SECProvider._has_value(sic):
            result["sic_code"] = str(
                sic
            ).strip()

        sic_description = submissions.get(
            "sicDescription"
        )

        if SECProvider._has_value(
            sic_description
        ):
            result["sic_description"] = str(
                sic_description
            ).strip()

        state = submissions.get(
            "stateOfIncorporation"
        )

        if SECProvider._has_value(state):
            result["state_of_incorporation"] = (
                str(state).strip()
            )

        fiscal_year_end = submissions.get(
            "fiscalYearEnd"
        )

        if SECProvider._has_value(
            fiscal_year_end
        ):
            result["fiscal_year_end"] = (
                str(fiscal_year_end).strip()
            )

    # =========================================================
    # Health Check
    # =========================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify SEC endpoint availability.
        """

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }

        try:
            async with httpx.AsyncClient(
                timeout=5.0,
                headers=headers,
            ) as client:

                response = await client.head(
                    self.COMPANY_TICKERS_URL
                )

                return response.status_code < 400

        except Exception:
            return False

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def _normalize_cik(
        value: Any,
    ) -> str:
        """
        Normalize SEC CIK.

        Leading zeroes are removed for canonical storage,
        except that zero itself remains ``0``.
        """

        if value is None:
            return ""

        value = str(value).strip()

        if not value:
            return ""

        value = value.lstrip("0")

        return value or "0"

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