"""
Embedding provider implementations.

Every provider must inherit EmbeddingProvider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from openai import OpenAI


# ============================================================
# Base Provider
# ============================================================

class EmbeddingProvider(ABC):
    """
    Base embedding provider.
    """

    model_name: str
    dimension: int

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Embed one text.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_batch(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Embed many texts.
        """
        raise NotImplementedError


# ============================================================
# OpenAI
# ============================================================

class OpenAIEmbeddingProvider(EmbeddingProvider):

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
    ):
        self.client = OpenAI(api_key=api_key)

        self.model_name = model

        if model == "text-embedding-3-small":
            self.dimension = 1536

        elif model == "text-embedding-3-large":
            self.dimension = 3072

        else:
            self.dimension = 1536

    def embed(self, text: str) -> List[float]:

        response = self.client.embeddings.create(
            model=self.model_name,
            input=text,
        )

        return response.data[0].embedding

    def embed_batch(
        self,
        texts: List[str],
    ) -> List[List[float]]:

        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts,
        )

        return [
            item.embedding
            for item in response.data
        ]


# ============================================================
# Ollama
# ============================================================

class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Placeholder.

    Replace with ollama package implementation later.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
    ):
        self.model_name = model
        self.dimension = 768

    def embed(self, text: str) -> List[float]:
        raise NotImplementedError(
            "Implement Ollama embeddings."
        )

    def embed_batch(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        raise NotImplementedError(
            "Implement Ollama embeddings."
        )


# ============================================================
# Voyage
# ============================================================

class VoyageEmbeddingProvider(EmbeddingProvider):

    def __init__(
        self,
        api_key: str,
        model: str = "voyage-3-large",
    ):
        self.api_key = api_key
        self.model_name = model
        self.dimension = 1024

    def embed(self, text: str):
        raise NotImplementedError(
            "Implement Voyage API."
        )

    def embed_batch(self, texts):
        raise NotImplementedError(
            "Implement Voyage API."
        )


# ============================================================
# HuggingFace / SentenceTransformer
# ============================================================

class SentenceTransformerProvider(EmbeddingProvider):
    """
    Local embedding model.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
    ):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

        self.model_name = model_name

        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str):
        return self.model.encode(
            text,
            normalize_embeddings=True,
        ).tolist()

    def embed_batch(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
        ).tolist()