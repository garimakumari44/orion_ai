# app/tools/news/article_search.py

from typing import List, Dict
from .news_client import NewsClient



class ArticleSearch:
    """
    Financial article retrieval engine.
    """


    def __init__(
        self,
        news_client: NewsClient
    ):

        self.news_client = news_client



    def search_company_news(
        self,
        company: str,
        limit: int = 10
    ) -> List[Dict]:


        articles = self.news_client.search_news(
            query=company,
            limit=limit
        )


        return self.rank_articles(
            articles
        )



    def rank_articles(
        self,
        articles: List[Dict]
    ) -> List[Dict]:


        """
        Simple relevance scoring.

        Later:
        - embeddings
        - reranker model
        - KG relevance
        """


        for article in articles:

            score = 0


            title = (
                article.get(
                    "title",
                    ""
                )
                .lower()
            )


            if any(
                word in title
                for word in [
                    "earnings",
                    "revenue",
                    "acquisition",
                    "lawsuit",
                    "guidance"
                ]
            ):
                score += 5


            if article.get(
                "source"
            ):
                score += 1


            article[
                "relevance_score"
            ] = score



        return sorted(
            articles,
            key=lambda x:
                x["relevance_score"],
            reverse=True
        )