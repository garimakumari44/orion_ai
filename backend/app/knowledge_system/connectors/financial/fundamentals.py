from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class FundamentalsConnector:
    """
    Company fundamental data connector.

    Provides:
    - financial statements
    - ratios
    - company metrics
    """


    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.example.com/fundamentals"
    ):

        self.api_key = api_key
        self.base_url = base_url



    async def get_company_profile(
        self,
        symbol: str
    ) -> Dict[str, Any]:

        url = (
            f"{self.base_url}/profile/"
            f"{symbol}"
        )


        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(url)

                response.raise_for_status()

                data = response.json()


            return {
                "type": "company_profile",
                "symbol": symbol,
                "data": data
            }


        except Exception as e:

            logger.error(
                "Profile fetch failed: %s",
                e
            )

            return {
                "symbol": symbol,
                "error": str(e)
            }



    async def get_financial_statements(
        self,
        symbol: str,
        statement_type: str = "income"
    ) -> Dict[str, Any]:

        """
        statement_type:
        - income
        - balance_sheet
        - cash_flow
        """


        url = (
            f"{self.base_url}/statements/"
            f"{symbol}"
        )


        params = {
            "type": statement_type
        }


        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(
                    url,
                    params=params
                )

                response.raise_for_status()

                data=response.json()


            return {
                "type": "financial_statement",
                "symbol": symbol,
                "statement": statement_type,
                "data": data
            }


        except Exception as e:

            logger.error(
                "Statement fetch failed: %s",
                e
            )

            return {
                "symbol": symbol,
                "error": str(e)
            }