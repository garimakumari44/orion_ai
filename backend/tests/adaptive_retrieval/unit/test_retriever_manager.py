"""
Unit tests for Retriever Components

Tests:
- BaseRetriever
- SparseRetriever
- MemoryRetriever
- BM25Retriever
- HybridRetriever
"""

import pytest
from uuid import uuid4

from app.adaptive_retrieval.retrievers.base import BaseRetriever
from app.adaptive_retrieval.retrievers.sparse import SparseRetriever
from app.adaptive_retrieval.retrievers.memory import MemoryRetriever
from app.adaptive_retrieval.retrievers.hybrid import HybridRetriever
from app.adaptive_retrieval.retrievers.bm25 import BM25Retriever

from app.knowledge_system.models.chunk import Chunk



# =====================================================
# Chunk Factory
# =====================================================

def create_chunk(
    text="sample text",
    index=0
):

    document_id = uuid4()

    return Chunk(
        id=uuid4(),
        document_id=document_id,
        text=text,
        chunk_index=index,
    )



# =====================================================
# Fixtures
# =====================================================

@pytest.fixture
def chunks():

    document_id = uuid4()

    return [

        Chunk(
            id=uuid4(),
            document_id=document_id,
            text="Python programming language",
            chunk_index=0,
        ),

        Chunk(
            id=uuid4(),
            document_id=document_id,
            text="Machine learning with neural networks",
            chunk_index=1,
        ),

        Chunk(
            id=uuid4(),
            document_id=document_id,
            text="Database indexing and retrieval",
            chunk_index=2,
        ),
    ]



# =====================================================
# Mock Document Store
# =====================================================

class MockDocumentStore:


    async def keyword_search(
        self,
        query,
        top_k,
        filters=None,
    ):

        return [

            create_chunk(
                text=f"Keyword result for {query}"
            )

        ][:top_k]



# =====================================================
# Base Retriever
# =====================================================

def test_base_retriever_is_abstract():

    with pytest.raises(TypeError):

        BaseRetriever()



# =====================================================
# Sparse Retriever
# =====================================================

@pytest.mark.asyncio
async def test_sparse_retriever():

    store = MockDocumentStore()


    retriever = SparseRetriever(
        document_store=store,
        top_k=5
    )


    results = await retriever.retrieve(
        query="python"
    )


    assert len(results) == 1

    assert (
        "Keyword result"
        in results[0].text
    )



# =====================================================
# Memory Retriever
# =====================================================

def test_memory_retriever_add_and_get(
    chunks
):

    memory = MemoryRetriever()


    memory.add(
        query="python",
        chunks=chunks
    )


    result = memory.retrieve(
        "python"
    )


    assert result == chunks

    assert memory.size == 1



def test_memory_retriever_missing_query():

    memory = MemoryRetriever()


    result = memory.retrieve(
        "unknown"
    )


    assert result is None



def test_memory_recent(
    chunks
):

    memory = MemoryRetriever()


    memory.add(
        "first",
        chunks
    )


    memory.add(
        "second",
        chunks
    )


    recent = memory.recent(
        limit=1
    )


    assert len(recent) == 1

    assert recent[0].query == "second"



def test_memory_clear(
    chunks
):

    memory = MemoryRetriever()


    memory.add(
        "test",
        chunks
    )


    memory.clear()


    assert memory.size == 0



# =====================================================
# BM25 Retriever
# =====================================================

def test_bm25_build_and_retrieve(
    chunks
):

    retriever = BM25Retriever()


    retriever.build_index(
        chunks
    )


    results = retriever.retrieve(
        "python",
        top_k=2
    )


    assert len(results) == 2

    assert (
        results[0].text
        ==
        "Python programming language"
    )



def test_bm25_without_index():

    retriever = BM25Retriever()


    with pytest.raises(RuntimeError):

        retriever.retrieve(
            "python"
        )



# =====================================================
# Hybrid Retriever
# =====================================================

class MockRetriever:


    def __init__(
        self,
        results
    ):

        self.results = results



    async def retrieve(
        self,
        query,
        top_k=10
    ):

        return self.results[:top_k]




@pytest.mark.asyncio
async def test_hybrid_retriever_rrf():


    chunk_a = create_chunk(
        "Result A"
    )


    chunk_b = create_chunk(
        "Result B"
    )


    dense = MockRetriever(
        [
            chunk_a,
            chunk_b
        ]
    )


    sparse = MockRetriever(
        [
            chunk_a
        ]
    )


    keyword = MockRetriever(
        [
            chunk_b
        ]
    )


    graph = MockRetriever(
        [
            chunk_a
        ]
    )


    retriever = HybridRetriever(
        dense=dense,
        sparse=sparse,
        keyword=keyword,
        graph=graph
    )


    results = await retriever.retrieve(
        "test",
        top_k=2
    )


    assert len(results) == 2


    # chunk_a appears in 3 sources
    # so it should rank first

    assert results[0].id == chunk_a.id



# =====================================================
# RRF Direct Test
# =====================================================

def test_rrf_scoring():


    retriever = HybridRetriever(
        None,
        None,
        None,
        None
    )


    chunk = create_chunk(
        "test"
    )


    result = retriever._rrf(
        [
            chunk
        ],
        top_k=1
    )


    assert len(result) == 1

    assert result[0].id == chunk.id