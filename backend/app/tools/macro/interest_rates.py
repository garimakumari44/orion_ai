"""
interest_rates.py

Interest Rate Macro Tool

Provides:
- Central bank rates
- Government bond yields
- Yield curve analysis
- Rate direction
- Monetary policy signals

Used by:
- Macro Agent
- Risk Agent
- Valuation Agent
- Investment Committee Agent
"""


from datetime import datetime
from typing import Dict, Any, Optional


from app.tools.base.base_tool import BaseTool
from app.tools.base.tool_result import ToolResult



class InterestRatesTool(BaseTool):

    name = "interest_rates"


    description = """
    Provides interest rate intelligence:

    - Policy rates
    - Treasury yields
    - Yield curve
    - Rate expectations
    - Monetary policy stance
    """



    def __init__(self, data_client=None):

        self.data_client = data_client



    async def execute(
        self,
        country: str = "US",
        maturity: Optional[str] = None,
        **kwargs
    ) -> ToolResult:


        try:

            data = await self.get_interest_rates(
                country,
                maturity
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




    async def get_interest_rates(
        self,
        country: str,
        maturity: Optional[str]
    ) -> Dict[str, Any]:


        """
        Production sources:

        - Federal Reserve
        - Treasury APIs
        - FRED
        - ECB
        - BOJ
        - RBI

        """


        if self.data_client:


            return await self.data_client.get_interest_rates(
                country=country,
                maturity=maturity
            )



        # Development mock response


        return {


            "country": country,


            "timestamp":
                datetime.utcnow().isoformat(),



            "rates": {



                "central_bank_rate": {


                    "value": 4.50,
                    "unit": "%",

                    "institution":
                    "Federal Reserve"

                },



                "treasury_yields": {


                    "2Y": {

                        "value": 4.10,
                        "unit": "%"

                    },


                    "10Y": {

                        "value": 4.25,
                        "unit": "%"

                    },


                    "30Y": {

                        "value": 4.55,
                        "unit": "%"

                    }


                },



                "yield_curve": {


                    "spread_10Y_2Y": {


                        "value":0.15,
                        "unit":"%"


                    },


                    "status":

                    "normal"


                }



            },



            "monetary_policy": {



                "direction":

                "neutral",



                "next_move_probability": {


                    "rate_cut":

                    0.62,


                    "rate_hike":

                    0.08,


                    "hold":

                    0.30

                }



            },



            "market_impact": {



                "equities":

                "positive",



                "growth_stocks":

                "benefiting",



                "bond_market":

                "stable"


            },


            "source":

            "interest-rate-provider"

        }