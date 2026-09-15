"""
Web Content Extractor

Transforms web pages into
structured research information.
"""

from typing import Dict, List
import requests
from bs4 import BeautifulSoup


from app.tools.base.base_tool import BaseTool
from app.tools.base.tool_result import ToolResult



class WebExtractorTool(BaseTool):


    name = "web_extractor"


    description = """
    Extract useful information
    from web pages.

    Used for:
    - financial reports
    - news articles
    - company pages
    """


    def execute(
        self,
        url: str
    ) -> ToolResult:


        try:

            content = self.extract(url)


            return ToolResult.success(
                data={
                    "url": url,
                    "content": content
                }
            )


        except Exception as e:

            return ToolResult.failure(
                error=str(e)
            )



    def extract(
        self,
        url: str
    ) -> Dict:


        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )


        response.raise_for_status()


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # remove noise

        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer"
            ]
        ):
            tag.extract()



        text = soup.get_text(
            separator=" ",
            strip=True
        )


        return {

            "title":
                soup.title.text
                if soup.title
                else None,


            "text":
                text,


            "word_count":
                len(text.split())

        }