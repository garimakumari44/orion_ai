"""
SEC Filing Search Tool

Searches SEC EDGAR filings.
"""

from typing import List, Dict, Optional

from app.tools.base.base_tool import BaseTool
from app.tools.base.tool_result import ToolResult
from app.tools.base.tool_context import ToolContext

from app.tools.sec.sec_client import SECClient


class FilingSearchTool(BaseTool):
    """
    Search SEC filings.

    Example:
        Input:
        {
            "ticker": "AAPL",
            "filing_type": "10-K"
        }

    Output:
        List of filings
    """

    name = "sec_filing_search"

    description = """
    Search SEC EDGAR filings by company ticker
    and filing type.
    """

    def __init__(self):
        self.sec_client = SECClient()


    async def execute(
        self,
        context: ToolContext,
        params: Dict
    ) -> ToolResult:

        ticker = params.get("ticker")

        filing_type = params.get(
            "filing_type",
            "10-K"
        )

        limit = params.get(
            "limit",
            5
        )


        if not ticker:
            return ToolResult(
                success=False,
                error="Ticker is required"
            )


        filings = await self.search_filings(
            ticker,
            filing_type,
            limit
        )


        return ToolResult(
            success=True,
            data=filings
        )


    async def search_filings(
        self,
        ticker: str,
        filing_type: str,
        limit: int = 5
    ) -> List[Dict]:

        company = await self.sec_client.get_company(
            ticker
        )


        if not company:
            return []


        cik = company["cik"]


        submissions = await self.sec_client.get_submissions(
            cik
        )


        results = []


        recent = submissions.get(
            "filings",
            {}
        ).get(
            "recent",
            {}
        )


        forms = recent.get(
            "form",
            []
        )

        accession = recent.get(
            "accessionNumber",
            []
        )

        dates = recent.get(
            "filingDate",
            []
        )

        documents = recent.get(
            "primaryDocument",
            []
        )


        for i, form in enumerate(forms):

            if form == filing_type:

                results.append(
                    {
                        "form": form,
                        "date": dates[i],
                        "accession": accession[i],
                        "document": documents[i],
                        "cik": cik
                    }
                )


            if len(results) >= limit:
                break


        return results