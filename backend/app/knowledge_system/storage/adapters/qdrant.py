"""
Qdrant Adapter

Handles vector storage and retrieval.
"""

from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


class QdrantAdapter:

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: str | None = None,
    ):
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
        )

    def upsert(
        self,
        collection: str,
        points: list[PointStruct],
    ):

        self.client.upsert(
            collection_name=collection,
            points=points,
        )

    def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 5,
    ):

        return self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
        )

    def delete(
        self,
        collection: str,
        ids: list[int],
    ):

        self.client.delete(
            collection_name=collection,
            points_selector=ids,
        )

    def collection_exists(
        self,
        collection: str,
    ) -> bool:

        collections = self.client.get_collections()

        return any(
            c.name == collection
            for c in collections.collections
        )

    def health(self) -> bool:

        try:
            self.client.get_collections()
            return True
        except Exception:
            return False