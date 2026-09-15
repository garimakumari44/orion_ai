from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class EstimatesConnector:
    """
    Analyst estimates connector.

    Provides:
    - earnings estimates
    - revenue estimates
    - analyst expectations
    """



    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.example.com/estimates"
    ):

        self.api_key = api_key
        self.base_url = base_url



    async def get_eps_estimates(
        self,
        symbol: str
    ) -> Dict[str, Any]:


        url = (
            f"{self.base_url}/eps/"
            f"{symbol}"
        )


        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(url)

                response.raise_for_status()

                data=response.json()


            return {
                "type": "eps_estimates",
                "symbol": symbol,
                "data": data
            }



        except Exception as e:

            logger.error(
                "EPS estimates failed: %s",
                e
            )

            return {
                "symbol": symbol,
                "error": str(e)
            }




    async def get_revenue_estimates(
        self,
        symbol: str
    ) -> Dict[str, Any]:

        url = (
            f"{self.base_url}/revenue/"
            f"{symbol}"
        )


        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(url)

                response.raise_for_status()

                data=response.json()


            return {
                "type": "revenue_estimates",
                "symbol": symbol,
                "data": data
            }


        except Exception as e:

            logger.error(
                "Revenue estimates failed: %s",
                e
            )

            return {
                "symbol": symbol,
                "error": str(e)
            }