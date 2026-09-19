"""
Elasticsearch Adapter

Responsibilities
----------------
- Full-text indexing
- Search
- Bulk indexing
- Document CRUD
"""

from __future__ import annotations

from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticsearchAdapter:
    """
    Thin Elasticsearch wrapper.
    """

    def __init__(
        self,
        hosts: str | list[str] = "http://localhost:9200",
        api_key: str | None = None,
    ):
        self.client = Elasticsearch(
            hosts=hosts,
            api_key=api_key,
        )

    def index(
        self,
        index: str,
        document: dict,
        doc_id: str | None = None,
    ):
        return self.client.index(
            index=index,
            id=doc_id,
            document=document,
        )

    def bulk_index(
        self,
        actions: list[dict],
    ):
        return bulk(
            self.client,
            actions,
        )

    def search(
        self,
        index: str,
        query: dict,
    ):
        return self.client.search(
            index=index,
            query=query,
        )

    def get(
        self,
        index: str,
        doc_id: str,
    ):
        return self.client.get(
            index=index,
            id=doc_id,
        )

    def delete(
        self,
        index: str,
        doc_id: str,
    ):
        return self.client.delete(
            index=index,
            id=doc_id,
        )

    def health(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False