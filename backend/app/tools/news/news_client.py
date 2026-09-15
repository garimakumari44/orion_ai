# app/tools/news/news_client.py

from typing import List, Dict, Optional
import requests
from datetime import datetime


class NewsClient:
    """
    Client for retrieving financial news articles.

    Supports:
    - NewsAPI
    - Financial news providers
    - Custom enterprise feeds
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://newsapi.org/v2"
    ):
        self.api_key = api_key
        self.base_url = base_url


    def search_news(
        self,
        query: str,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict]:

        """
        Search news articles.

        Returns normalized article format.
        """

        if not self.api_key:
            return self._mock_articles(query)


        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": self.api_key
        }


        response = requests.get(
            f"{self.base_url}/everything",
            params=params,
            timeout=10
        )


        response.raise_for_status()

        data = response.json()

        return [
            self._normalize_article(article)
            for article in data.get("articles", [])
        ]


    def _normalize_article(
        self,
        article: Dict
    ) -> Dict:


        return {

            "title": article.get("title"),

            "summary": article.get(
                "description"
            ),

            "content": article.get(
                "content"
            ),

            "source": article.get(
                "source",
                {}
            ).get("name"),

            "url": article.get("url"),

            "published_at":
                article.get(
                    "publishedAt"
                ),

            "retrieved_at":
                datetime.utcnow().isoformat()
        }



    def _mock_articles(
        self,
        query:str
    ) -> List[Dict]:


        return [

            {
                "title":
                f"{query} announces strong quarterly growth",

                "summary":
                "Company reported better than expected results.",

                "content":
                "Revenue increased while margins improved.",

                "source":
                "Mock Financial News",

                "url":
                "https://example.com",

                "published_at":
                datetime.utcnow().isoformat()
            }

        ]