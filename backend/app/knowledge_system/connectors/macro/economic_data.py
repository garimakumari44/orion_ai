from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class MacroEconomicClient:
    """
    Client for retrieving macroeconomic indicators.

    Responsible only for data acquisition.
    No analysis or forecasting.
    """

    BASE_URL = "https://api.example.com/macro"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 20,
    ):
        self.api_key = api_key
        self.timeout = timeout

    async def _request(
        self,
        endpoint: str,
        params: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        headers = {}

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                headers=headers,
            )

            response.raise_for_status()

            return response.json()


    async def get_gdp(
        self,
        country: str = "US",
    ) -> Dict[str, Any]:

        return await self._request(
            "gdp",
            {
                "country": country
            }
        )


    async def get_inflation(
        self,
        country: str = "US",
    ) -> Dict[str, Any]:

        return await self._request(
            "inflation",
            {
                "country": country
            }
        )


    async def get_unemployment(
        self,
        country: str = "US",
    ) -> Dict[str, Any]:

        return await self._request(
            "unemployment",
            {
                "country": country
            }
        )


    async def get_indicator(
        self,
        indicator: str,
        country: str = "US",
    ) -> Dict[str, Any]:

        return await self._request(
            "indicator",
            {
                "name": indicator,
                "country": country,
            }
        )