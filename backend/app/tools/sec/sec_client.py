"""
SEC Client

Low level SEC EDGAR API client.
"""

from typing import Dict, Optional

import httpx


class SECClient:

    BASE_URL = "https://data.sec.gov"


    HEADERS = {
        "User-Agent":
        "Orion AI Equity Research System contact@example.com"
    }


    def __init__(self):

        self.client = httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=30
        )


    async def close(self):

        await self.client.aclose()



    async def get_company(
        self,
        ticker: str
    ) -> Optional[Dict]:

        """
        Resolve ticker to company CIK.

        Example:
        AAPL -> Apple CIK
        """

        url = (
            f"{self.BASE_URL}/files/"
            "company_tickers.json"
        )


        response = await self.client.get(
            url
        )

        response.raise_for_status()


        data = response.json()


        ticker = ticker.upper()


        for company in data.values():

            if company["ticker"] == ticker:

                return {
                    "ticker":
                        company["ticker"],

                    "title":
                        company["title"],

                    "cik":
                        str(company["cik_str"])
                        .zfill(10)
                }


        return None




    async def get_submissions(
        self,
        cik: str
    ) -> Dict:

        """
        Fetch SEC filing history.
        """


        url = (
            f"{self.BASE_URL}/submissions/"
            f"CIK{cik}.json"
        )


        response = await self.client.get(
            url
        )


        response.raise_for_status()


        return response.json()



    async def get_company_facts(
        self,
        cik: str
    ) -> Dict:

        """
        Retrieve XBRL company facts.
        """

        url = (
            f"{self.BASE_URL}/api/xbrl/"
            f"companyfacts/CIK{cik}.json"
        )


        response = await self.client.get(
            url
        )


        response.raise_for_status()


        return response.json()



    async def download_document(
        self,
        url: str
    ) -> str:

        """
        Download raw filing document.
        """

        response = await self.client.get(
            url
        )


        response.raise_for_status()


        return response.text