"""
economic_data.py

Macro Economic Data Tool

Responsible for:
- GDP growth
- Employment data
- Unemployment
- Economic cycles
- Consumer spending
- Manufacturing activity
- Economic indicators aggregation

Used by:
- Macro Agent
- Risk Agent
- Investment Committee Agent
"""

from datetime import datetime
from typing import Dict, Any, Optional

from app.tools.base.base_tool import BaseTool
from app.tools.base.tool_result import ToolResult


class EconomicDataTool(BaseTool):

    name = "economic_data"

    description = """
    Provides macroeconomic indicators including:
    GDP, employment,
    unemployment,
    consumer activity,
    manufacturing,
    economic growth metrics.
    """

    def __init__(self, data_client=None):
        """
        data_client:
            External API client
            (FRED, World Bank, IMF etc.)
        """

        self.data_client = data_client


    async def execute(
        self,
        country: str = "US",
        indicator: Optional[str] = None,
        period: Optional[str] = None,
        **kwargs
    ) -> ToolResult:


        try:

            data = await self.fetch_economic_data(
                country=country,
                indicator=indicator,
                period=period
            )


            return ToolResult.success(
                tool=self.name,
                data=data
            )


        except Exception as e:

            return ToolResult.failure(
                tool=self.name,
                error=str(e)
            )



    async def fetch_economic_data(
        self,
        country: str,
        indicator: Optional[str],
        period: Optional[str]
    ) -> Dict[str, Any]:


        """
        Fetch economic indicators.

        Production:
        Replace mock layer with:

        - FRED API
        - World Bank API
        - IMF API
        - OECD API

        """


        if self.data_client:

            return await self.data_client.get_macro_data(
                country=country,
                indicator=indicator,
                period=period
            )


        # Mock data for development

        return {

            "country": country,

            "timestamp":
                datetime.utcnow().isoformat(),


            "economic_indicators": {


                "GDP_growth": {

                    "value": 2.4,
                    "unit": "%",
                    "period": "2026-Q1"

                },


                "unemployment_rate": {

                    "value": 4.1,
                    "unit": "%"

                },


                "consumer_spending_growth": {

                    "value": 3.2,
                    "unit": "%"

                },


                "manufacturing_PMI": {

                    "value": 51.8,
                    "status": "expansion"

                },


                "economic_cycle": {

                    "phase": "mid_cycle",
                    "confidence": 0.78

                }

            },


            "source":

            "macro-economic-data-provider"

        }