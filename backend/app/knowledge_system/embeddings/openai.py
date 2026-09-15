"""
OpenAI embedding provider.
"""

from __future__ import annotations

from typing import List

from .base import BaseEmbeddingModel
from .models import EmbeddingConfig


class OpenAIEmbedding(BaseEmbeddingModel):
    """
    OpenAI embedding model.
    """

    def __init__(self, config: EmbeddingConfig):
        self.config = config

        # Initialize your OpenAI client here.
        # Example:
        # from openai import AsyncOpenAI
        # self.client = AsyncOpenAI(api_key=...)

    @property
    def provider(self) -> str:
        return "openai"

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
        # Example implementation:
        #
        # response = await self.client.embeddings.create(
        #     model=self.config.model_name,
        #     input=texts,
        # )
        #
        # return [item.embedding for item in response.data]

        raise NotImplementedError(
            "OpenAI embedding implementation not yet configured."
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