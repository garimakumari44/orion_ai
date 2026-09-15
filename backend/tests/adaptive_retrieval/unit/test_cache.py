"""
Unit tests for RetrievalCache and CacheManager.

Tests:
- cache key generation
- set/get
- contains
- invalidate
- clear
- retriever isolation
- query normalization
- TTL expiration
- custom cache manager injection
"""

from __future__ import annotations

import time
from app.adaptive_retrieval.cache.cache_manager  import CacheManager
from app.adaptive_retrieval.cache.retrieval_cache  import RetrievalCache


# ============================================================
# RetrievalCache
# ============================================================


def test_make_key_is_deterministic():
    key1 = RetrievalCache.make_key(
        "dense",
        "What is AI?",
    )

    key2 = RetrievalCache.make_key(
        "dense",
        "What is AI?",
    )

    assert key1 == key2


def test_make_key_normalizes_query():
    key1 = RetrievalCache.make_key(
        "dense",
        "Hello World",
    )

    key2 = RetrievalCache.make_key(
        "dense",
        "  hello world   ",
    )

    assert key1 == key2


def test_make_key_differs_by_retriever():
    dense = RetrievalCache.make_key(
        "dense",
        "python",
    )

    bm25 = RetrievalCache.make_key(
        "bm25",
        "python",
    )

    assert dense != bm25


def test_set_and_get():
    cache = RetrievalCache()

    docs = [
        {"id": 1},
        {"id": 2},
    ]

    cache.set(
        "dense",
        "python",
        docs,
    )

    assert cache.get(
        "dense",
        "python",
    ) == docs


def test_get_missing_returns_none():
    cache = RetrievalCache()

    assert (
        cache.get(
            "dense",
            "missing",
        )
        is None
    )


def test_contains():
    cache = RetrievalCache()

    cache.set(
        "dense",
        "query",
        [{"id": 1}],
    )

    assert cache.contains(
        "dense",
        "query",
    )


def test_contains_false_for_missing():
    cache = RetrievalCache()

    assert not cache.contains(
        "dense",
        "missing",
    )


def test_invalidate():
    cache = RetrievalCache()

    cache.set(
        "dense",
        "query",
        [{"id": 1}],
    )

    assert cache.invalidate(
        "dense",
        "query",
    )

    assert not cache.contains(
        "dense",
        "query",
    )


def test_invalidate_missing_returns_false():
    cache = RetrievalCache()

    assert not cache.invalidate(
        "dense",
        "missing",
    )


def test_clear():
    cache = RetrievalCache()

    cache.set(
        "dense",
        "a",
        [1],
    )

    cache.set(
        "bm25",
        "b",
        [2],
    )

    cache.clear()

    assert not cache.contains(
        "dense",
        "a",
    )

    assert not cache.contains(
        "bm25",
        "b",
    )


def test_retrievers_are_isolated():
    cache = RetrievalCache()

    dense_docs = [{"dense": True}]
    bm25_docs = [{"bm25": True}]

    cache.set(
        "dense",
        "python",
        dense_docs,
    )

    cache.set(
        "bm25",
        "python",
        bm25_docs,
    )

    assert (
        cache.get(
            "dense",
            "python",
        )
        == dense_docs
    )

    assert (
        cache.get(
            "bm25",
            "python",
        )
        == bm25_docs
    )


def test_query_normalization_lookup():
    cache = RetrievalCache()

    docs = [{"id": 1}]

    cache.set(
        "dense",
        "Hello World",
        docs,
    )

    assert (
        cache.get(
            "dense",
            "  hello world ",
        )
        == docs
    )


def test_ttl_expiration():
    cache = RetrievalCache(ttl=1)

    cache.set(
        "dense",
        "query",
        [{"id": 1}],
    )

    time.sleep(1.2)

    assert (
        cache.get(
            "dense",
            "query",
        )
        is None
    )


def test_custom_cache_manager():
    manager = CacheManager()

    cache = RetrievalCache(
        cache=manager,
    )

    docs = [{"id": 99}]

    cache.set(
        "dense",
        "custom",
        docs,
    )

    assert (
        cache.get(
            "dense",
            "custom",
        )
        == docs
    )


# ============================================================
# CacheManager
# ============================================================


def test_cache_manager_set_get():
    manager = CacheManager()

    manager.set(
        "key",
        "value",
    )

    assert manager.get("key") == "value"


def test_cache_manager_delete():
    manager = CacheManager()

    manager.set(
        "key",
        "value",
    )

    assert manager.delete("key")

    assert manager.get("key") is None


def test_cache_manager_contains():
    manager = CacheManager()

    manager.set(
        "key",
        123,
    )

    assert manager.contains("key")


def test_cache_manager_clear():
    manager = CacheManager()

    manager.set("a", 1)
    manager.set("b", 2)

    manager.clear()

    assert manager.size() == 0


def test_cache_manager_keys():
    manager = CacheManager()

    manager.set("a", 1)
    manager.set("b", 2)

    keys = manager.keys()

    assert "a" in keys
    assert "b" in keys


def test_cache_manager_size():
    manager = CacheManager()

    assert manager.size() == 0

    manager.set("a", 1)

    assert manager.size() == 1


def test_cache_manager_cleanup():
    manager = CacheManager(default_ttl=1)

    manager.set(
        "temporary",
        123,
    )

    time.sleep(1.2)

    removed = manager.cleanup()

    assert removed == 1
    assert manager.size() == 0