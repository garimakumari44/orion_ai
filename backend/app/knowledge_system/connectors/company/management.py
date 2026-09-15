from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class ManagementClient:
    """
    Retrieves company management information.
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



    async def get_executives(
        self,
        ticker: str,
    ) -> Dict[str, Any]:

        """
        Returns executive team.
        """

        return await self._request(
            "executives",
            {
                "ticker": ticker
            }
        )



    async def get_board_members(
        self,
        ticker: str,
    ) -> Dict[str, Any]:

        """
        Returns board information.
        """

        return await self._request(
            "board",
            {
                "ticker": ticker
            }
        )



    async def get_management_history(
        self,
        ticker: str,
    ) -> Dict[str, Any]:

        """
        Returns leadership changes.
        """

        return await self._request(
            "management-history",
            {
                "ticker": ticker
            }
        )