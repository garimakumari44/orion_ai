from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)


class MarketDataConnector:
    """
    Financial market data acquisition connector.

    Responsible for:
    - price data
    - candles
    - volume
    - market metrics
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.example.com/market"
    ):
        self.api_key = api_key
        self.base_url = base_url


    async def get_quote(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Get latest quote.
        """

        url = f"{self.base_url}/quote/{symbol}"


        headers = {}

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )


        try:
            async with httpx.AsyncClient() as client:

                response = await client.get(
                    url,
                    headers=headers
                )

                response.raise_for_status()

                data = response.json()


            return {
                "type": "market_quote",
                "symbol": symbol,
                "price": data.get("price"),
                "change": data.get("change"),
                "change_percent": data.get(
                    "change_percent"
                ),
                "volume": data.get("volume"),
                "timestamp": datetime.utcnow().isoformat(),
            }


        except Exception as e:

            logger.error(
                "Market quote failed: %s",
                e
            )

            return {
                "type": "market_quote",
                "symbol": symbol,
                "error": str(e)
            }



    async def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y"
    ) -> Dict[str, Any]:

        """
        Historical OHLC data.
        """


        url = (
            f"{self.base_url}/history/"
            f"{symbol}"
        )


        params = {
            "period": period
        }


        try:

            async with httpx.AsyncClient() as client:

                response = await client.get(
                    url,
                    params=params
                )

                response.raise_for_status()

                data = response.json()


            return {
                "type": "historical_prices",
                "symbol": symbol,
                "period": period,
                "data": data,
            }


        except Exception as e:

            logger.error(
                "Historical prices failed: %s",
                e
            )

            return {
                "symbol": symbol,
                "error": str(e)
            }