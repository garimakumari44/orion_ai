from __future__ import annotations

from typing import Any

from services.company_search_service import CompanySearchService


class SearchEngine:
    """
    Central search engine for company discovery.

    Responsibilities:
    - Receive search requests
    - Delegate to CompanySearchService
    - Apply pagination
    - Apply sorting
    - Return standardized response
    """

    def __init__(self) -> None:
        self.company_service = CompanySearchService()

    async def search_companies(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search companies from all providers.
        """

        companies = await self.company_service.search(query)

        total = len(companies)

        results = companies[offset : offset + limit]

        return {
            "query": query,
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results,
        }

    async def autocomplete(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Lightweight autocomplete endpoint.
        """

        companies = await self.company_service.search(query)

        return companies[:limit]

    async def search_by_symbol(
        self,
        symbol: str,
    ) -> dict[str, Any] | None:
        """
        Find a company by ticker symbol.
        """

        companies = await self.company_service.search(symbol)

        symbol = symbol.upper()

        for company in companies:
            if company.get("ticker", "").upper() == symbol:
                return company

        return None