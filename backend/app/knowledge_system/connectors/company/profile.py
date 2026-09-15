from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class CompanyProfileClient:
    """
    Retrieves company profile information.

    Data sources can include:
    - SEC
    - Company APIs
    - Financial data providers
    """

    BASE_URL = "https://api.example.com/company"


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



    async def get_profile(
        self,
        ticker: str,
    ) -> Dict[str, Any]:

        """
        Fetch company profile.
        """

        return await self._request(
            "profile",
            {
                "ticker": ticker
            }
        )



    async def get_industry(
        self,
        ticker: str,
    ) -> Dict[str, Any]:

        """
        Fetch sector and industry classification.
        """

        return await self._request(
            "industry",
            {
                "ticker": ticker
            }
        )



    async def get_business_description(
        self,
        ticker: str,
    ) -> Dict[str, Any]:

        return await self._request(
            "description",
            {
                "ticker": ticker
            }
        )