from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class GuidanceClient:
    """
    Company earnings guidance connector.

    Handles:
    - Revenue guidance
    - Margin outlook
    - Growth expectations
    - Management forecasts
    """


    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "default"
    ):

        self.api_key = api_key
        self.provider = provider



    async def fetch_guidance(
        self,
        ticker: str,
        quarter: str,
        year: int
    ) -> Dict[str, Any]:

        """
        Fetch company forward guidance.
        """


        logger.info(
            "Fetching guidance %s %s %s",
            ticker,
            quarter,
            year
        )


        return {

            "ticker": ticker,

            "period": {
                "quarter": quarter,
                "year": year
            },


            "guidance": {

                "revenue": {
                    "low": 100,
                    "high": 110,
                    "currency": "USD"
                },


                "gross_margin": {
                    "low": 45,
                    "high": 48
                },


                "operating_margin": {
                    "low": 20,
                    "high": 22
                },


                "growth_commentary":
                    (
                        "Management expects "
                        "continued demand growth."
                    )
            }

        }



    async def extract_guidance_points(
        self,
        transcript: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract guidance statements
        from earnings transcript.
        """


        guidance_points = []


        sections = transcript.get(
            "sections",
            []
        )


        for section in sections:

            text = section.get(
                "content",
                ""
            )


            keywords = [
                "expect",
                "forecast",
                "guidance",
                "outlook",
                "target"
            ]


            if any(
                word in text.lower()
                for word in keywords
            ):

                guidance_points.append(
                    {
                        "speaker":
                            section.get(
                                "speaker"
                            ),

                        "statement":
                            text
                    }
                )


        return guidance_points



    def normalize_guidance(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert guidance into
        knowledge system format.
        """


        return {

            "document_type":
                "company_guidance",


            "metadata": {

                "ticker":
                    data.get(
                        "ticker"
                    ),

                "period":
                    data.get(
                        "period"
                    )
            },


            "content":
                data.get(
                    "guidance"
                )
        }