"""
Web Search Tool

Provides web search capabilities for research agents.
Used by:
- Company Agent
- News Agent
- Industry Agent
- Macro Agent
"""

from typing import List, Dict, Optional
import requests

from app.tools.base.base_tool import BaseTool
from app.tools.base.tool_result import ToolResult


class WebSearchTool(BaseTool):
    """
    General purpose web search tool.
    """

    name = "web_search"
    description = """
    Search the internet for relevant information.
    Useful for:
    - company research
    - financial news
    - industry trends
    - market updates
    """


    def __init__(
        self,
        api_key: Optional[str] = None,
        search_engine: str = "duckduckgo"
    ):
        self.api_key = api_key
        self.search_engine = search_engine


    def execute(
        self,
        query: str,
        limit: int = 5
    ) -> ToolResult:
        """
        Execute search request.
        """

        try:

            results = self._search(
                query=query,
                limit=limit
            )

            return ToolResult.success(
                data={
                    "query": query,
                    "results": results
                }
            )


        except Exception as e:

            return ToolResult.failure(
                error=str(e)
            )


    def _search(
        self,
        query: str,
        limit: int
    ) -> List[Dict]:


        """
        Internal search implementation.

        Replace this with:
        - Bing API
        - SerpAPI
        - Tavily
        - Brave Search API
        """

        url = (
            "https://api.duckduckgo.com/"
        )


        params = {
            "q": query,
            "format": "json",
            "no_html": 1
        }


        response = requests.get(
            url,
            params=params,
            timeout=10
        )


        response.raise_for_status()


        data = response.json()


        results = []


        for item in data.get(
            "RelatedTopics",
            []
        )[:limit]:

            if isinstance(item, dict):

                results.append(
                    {
                        "title":
                            item.get("Text"),

                        "url":
                            item.get("FirstURL"),

                        "snippet":
                            item.get("Text")
                    }
                )


        return results