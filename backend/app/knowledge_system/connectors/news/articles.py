from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class NewsArticle:
    """
    Standardized news article object
    used by knowledge ingestion pipeline.
    """

    title: str

    content: str

    url: Optional[str] = None

    source: Optional[str] = None

    published_at: Optional[datetime] = None

    authors: List[str] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)


class ArticleParser:
    """
    Converts raw news API responses
    into normalized NewsArticle objects.
    """

    def parse(
        self,
        raw_article: dict
    ) -> NewsArticle:

        return NewsArticle(

            title=self.clean_text(
                raw_article.get("title", "")
            ),

            content=self.clean_text(
                raw_article.get(
                    "content",
                    raw_article.get("description", "")
                )
            ),

            url=raw_article.get("url"),

            source=self.extract_source(
                raw_article
            ),

            published_at=self.parse_date(
                raw_article.get(
                    "publishedAt"
                )
            ),

            authors=raw_article.get(
                "authors",
                []
            ),

            metadata={
                "raw": raw_article
            }
        )


    def clean_text(
        self,
        text: str
    ) -> str:

        if not text:
            return ""

        return (
            text
            .replace("\n", " ")
            .strip()
        )


    def extract_source(
        self,
        article: dict
    ):

        source = article.get(
            "source"
        )

        if isinstance(source, dict):
            return source.get(
                "name"
            )

        return source


    def parse_date(
        self,
        value
    ):

        if not value:
            return None

        try:
            return datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00"
                )
            )

        except Exception:
            return None