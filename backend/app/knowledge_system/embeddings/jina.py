"""
Jina AI embedding provider.
"""

from __future__ import annotations

from typing import List

from .base import BaseEmbeddingModel
from .models import EmbeddingConfig


class JinaEmbedding(BaseEmbeddingModel):
    """
    Jina embedding model.
    """

    def __init__(self, config: EmbeddingConfig):
        self.config = config

        # Initialize Jina client here.
        #
        # Example:
        # import httpx
        # self.client = httpx.AsyncClient()

    @property
    def provider(self) -> str:
        return "jina"

    @property
    def dimension(self) -> int:
        return self.config.dimension

    async def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Embed multiple documents.
        """
        # Example:
        #
        # POST https://api.jina.ai/v1/embeddings
        #
        # return embeddings

        raise NotImplementedError(
            "Jina embedding implementation not yet configured."
        )

    async def embed_query(
        self,
        text: str,
    ) -> List[float]:
        """
        Embed a single query.
        """
        vectors = await self.embed_documents([text])
        return vectors[0]