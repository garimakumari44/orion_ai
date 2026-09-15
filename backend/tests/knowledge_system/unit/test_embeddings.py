"""
Unit tests for the embedding subsystem.
"""

from __future__ import annotations

import pytest

from app.knowledge_system.embeddings.base import BaseEmbeddingModel
from app.knowledge_system.embeddings.batching import BatchProcessor
from app.knowledge_system.embeddings.cache import EmbeddingCache
from app.knowledge_system.embeddings.factory import EmbeddingFactory
from app.knowledge_system.embeddings.manager import EmbeddingManager
from app.knowledge_system.embeddings.models import (
    EmbeddingConfig,
    EmbeddingResult,
)


class DummyEmbedding(BaseEmbeddingModel):
    @property
    def provider(self) -> str:
        return "dummy"

    @property
    def dimension(self) -> int:
        return 3

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [[float(len(t)), 1.0, 2.0] for t in texts]

    async def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return [float(len(text)), 1.0, 2.0]


# ---------------------------------------------------------------------
# EmbeddingConfig
# ---------------------------------------------------------------------


def test_embedding_config_defaults():
    config = EmbeddingConfig(
        provider="dummy",
        model_name="test-model",
        dimension=3,
    )

    assert config.provider == "dummy"
    assert config.model_name == "test-model"
    assert config.dimension == 3
    assert config.batch_size == 32
    assert config.normalize is True


def test_embedding_result():
    result = EmbeddingResult(
        text="hello",
        embedding=[1.0, 2.0, 3.0],
    )

    assert result.text == "hello"
    assert result.embedding == [1.0, 2.0, 3.0]


# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------


def test_cache_set_get():
    cache = EmbeddingCache()

    cache.set("hello", [1.0, 2.0])

    assert cache.contains("hello")
    assert cache.get("hello") == [1.0, 2.0]


def test_cache_remove():
    cache = EmbeddingCache()

    cache.set("abc", [5.0])

    cache.remove("abc")

    assert not cache.contains("abc")
    assert cache.get("abc") is None


def test_cache_clear():
    cache = EmbeddingCache()

    cache.set("a", [1.0])
    cache.set("b", [2.0])

    cache.clear()

    assert len(cache) == 0


# ---------------------------------------------------------------------
# Batch Processor
# ---------------------------------------------------------------------


def test_batch_processor():
    processor = BatchProcessor(batch_size=3)

    batches = list(processor(range(8)))

    assert batches == [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7],
    ]


def test_invalid_batch_size():
    with pytest.raises(ValueError):
        BatchProcessor(0)


# ---------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------


def test_manager_register_get():
    manager = EmbeddingManager()

    provider = DummyEmbedding()

    manager.register(provider)

    assert manager.get("dummy") is provider
    assert manager.providers == ["dummy"]


def test_manager_unregister():
    manager = EmbeddingManager()

    provider = DummyEmbedding()

    manager.register(provider)
    manager.unregister("dummy")

    assert manager.providers == []


def test_manager_unknown_provider():
    manager = EmbeddingManager()

    with pytest.raises(ValueError):
        manager.get("missing")


# ---------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------


def test_factory_create():
    factory = EmbeddingFactory()

    factory.register(
        "dummy",
        lambda cfg: DummyEmbedding(),
    )

    config = EmbeddingConfig(
        provider="dummy",
        model_name="model",
        dimension=3,
    )

    model = factory.create(config)

    assert isinstance(model, DummyEmbedding)


def test_factory_unknown():
    factory = EmbeddingFactory()

    config = EmbeddingConfig(
        provider="unknown",
        model_name="x",
        dimension=3,
    )

    with pytest.raises(ValueError):
        factory.create(config)


# ---------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_query():
    model = DummyEmbedding()

    vector = await model.embed_query("hello")

    assert vector == [5.0, 1.0, 2.0]


@pytest.mark.asyncio
async def test_embed_documents():
    model = DummyEmbedding()

    vectors = await model.embed_documents(
        [
            "hi",
            "hello",
        ]
    )

    assert vectors == [
        [2.0, 1.0, 2.0],
        [5.0, 1.0, 2.0],
    ]