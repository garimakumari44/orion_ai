from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class InterestRateClient:
    """
    Retrieves interest rate information.

    Examples:
    - Federal Funds Rate
    - ECB Rate
    - Policy Rates
    - Treasury yields
    """

    BASE_URL = "https://api.example.com/rates"


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
    ):

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



    async def get_policy_rate(
        self,
        country: str = "US",
    ) -> Dict[str, Any]:

        return await self._request(
            "policy-rate",
            {
                "country": country
            }
        )



    async def get_yield_curve(
        self,
        country: str = "US",
    ) -> Dict[str, Any]:

        return await self._request(
            "yield-curve",
            {
                "country": country
            }
        )



    async def get_rate_history(
        self,
        rate_name: str,
        period: str = "5y",
    ) -> Dict[str, Any]:

        return await self._request(
            "history",
            {
                "rate": rate_name,
                "period": period,
            }
        )