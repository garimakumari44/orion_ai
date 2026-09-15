from __future__ import annotations

import logging
from typing import List, Optional

import httpx


from .articles import (
    NewsArticle,
    ArticleParser
)


logger = logging.getLogger(__name__)


class NewsClient:
    """
    News data acquisition connector.

    Fetches raw news and converts
    into Knowledge System objects.
    """


    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://newsapi.org/v2"
    ):

        self.api_key = api_key

        self.base_url = base_url

        self.parser = ArticleParser()


    async def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[NewsArticle]:

        """
        Search news articles.
        """

        if not self.api_key:
            logger.warning(
                "No news API key configured"
            )

            return []


        params = {

            "q": query,

            "pageSize": limit,

            "apiKey": self.api_key
        }


        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=20
            )


            response.raise_for_status()


            data = response.json()



        articles = []


        for item in data.get(
            "articles",
            []
        ):

            article = self.parser.parse(
                item
            )

            articles.append(
                article
            )


        return articles



    async def get_company_news(
        self,
        company: str,
        limit: int = 10
    ) -> List[NewsArticle]:

        """
        Company focused news retrieval.

        Example:
        Apple
        Nvidia
        Microsoft
        """

        return await self.search(
            query=company,
            limit=limit
        )