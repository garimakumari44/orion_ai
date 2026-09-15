from __future__ import annotations

from typing import Any

from .base import BaseProvider


class CrunchbaseProvider(BaseProvider):
    """
    Crunchbase company-data provider.
    """

    name = "crunchbase"

    async def search_company(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        if not isinstance(query, str):
            raise TypeError(
                "Crunchbase company search query must be a string."
            )

        query = query.strip()

        if not query:
            return []

        # TODO: implement Crunchbase API
        return []

    async def list_companies(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            return []

        if offset < 0:
            offset = 0

        # TODO: implement Crunchbase bulk API
        return []

    async def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        if not isinstance(symbol, str):
            raise TypeError(
                "Crunchbase company identifier must be a string."
            )

        symbol = symbol.strip()

        if not symbol:
            return {}

        return {
            "company_id": symbol,
            "source": self.name,
        }

    async def health_check(
        self,
    ) -> bool:
        """
        Crunchbase is currently a placeholder provider.

        Return False until real API connectivity is implemented.
        """
        return False