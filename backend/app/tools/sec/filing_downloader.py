"""
SEC Filing Downloader Tool

Downloads SEC filing documents from EDGAR.
"""


import os
from pathlib import Path
from typing import Dict

import httpx


from app.tools.base.base_tool import BaseTool
from app.tools.base.tool_result import ToolResult
from app.tools.base.tool_context import ToolContext



class FilingDownloaderTool(BaseTool):

    name = "sec_filing_downloader"


    description = """
    Download SEC filing documents.
    """



    SEC_ARCHIVE_URL = (
        "https://www.sec.gov/Archives"
    )


    def __init__(self):

        self.storage_path = Path(
            "data/sec_filings"
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True
        )



    async def execute(
        self,
        context: ToolContext,
        params: Dict
    ) -> ToolResult:


        cik = params.get("cik")
        accession = params.get(
            "accession"
        )
        document = params.get(
            "document"
        )


        if not all(
            [
                cik,
                accession,
                document
            ]
        ):

            return ToolResult(
                success=False,
                error=(
                    "cik, accession "
                    "and document required"
                )
            )


        file_path = await self.download(
            cik,
            accession,
            document
        )


        return ToolResult(
            success=True,
            data={
                "file_path": str(file_path)
            }
        )



    async def download(
        self,
        cik: str,
        accession: str,
        document: str
    ):


        accession_clean = accession.replace(
            "-",
            ""
        )


        url = (
            f"{self.SEC_ARCHIVE_URL}/edgar/data/"
            f"{int(cik)}/"
            f"{accession_clean}/"
            f"{document}"
        )


        filename = (
            self.storage_path /
            document
        )


        headers = {
            "User-Agent":
            "Orion AI Research Agent contact@example.com"
        }


        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                headers=headers
            )


            response.raise_for_status()


            filename.write_bytes(
                response.content
            )


        return filename