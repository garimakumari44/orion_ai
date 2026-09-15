"""
Knowledge System -> Adaptive Retrieval Integration Tests

Tests:

Knowledge System
    indexing
    embeddings
    storage

Adaptive Retrieval
    retrievers
    planner
    retrieval manager
"""


import pytest
from datetime import datetime


# -----------------------------
# Knowledge System
# -----------------------------

from app.knowledge_system.indexing.vector_index import (
    VectorIndex,
)

from app.knowledge_system.indexing.keyword_index import (
    KeywordIndex,
)

from app.knowledge_system.indexing.metadata_index import (
    MetadataIndex,
)

from app.knowledge_system.indexing.graph_index import (
    GraphIndex,
)

from app.knowledge_system.indexing.temporal_index import (
    TemporalIndex,
)


from app.knowledge_system.storage.stores.document_store import (
    InMemoryDocumentStore,
)

from app.knowledge_system.storage.stores.vector_store import (
    InMemoryVectorStore,
)



# -----------------------------
# Adaptive Retrieval
# -----------------------------

from app.adaptive_retrieval.planner.query_analyzer import (
    QueryAnalyzer,
)

from app.adaptive_retrieval.planner.intent_classifier import (
    RetrievalIntent,
)

from app.adaptive_retrieval.planner.retrieval_planner import (
    RetrievalPlanner,
)

from app.adaptive_retrieval.models.query import (
    Query,
)



# ==========================================================
# Fake Embedding Provider
# ==========================================================


class FakeEmbeddingModel:


    async def embed_query(self,text):

        """
        deterministic fake vector
        """

        return [
            float(len(text)),
            0.5,
            0.2
        ]


    async def embed_documents(self,texts):

        return [
            [
                float(len(t)),
                0.5,
                0.2
            ]
            for t in texts
        ]



# ==========================================================
# Indexing Tests
# ==========================================================


def test_vector_index_add_and_search():

    index = VectorIndex()


    index.add(
        document_id="doc1",
        embedding=[
            1,
            0,
            0
        ],
        metadata={
            "source":"github"
        }
    )


    results = index.search(
        [
            1,
            0,
            0
        ]
    )


    assert len(results)==1

    assert results[0]["id"]=="doc1"



def test_keyword_index():

    index = KeywordIndex()


    index.add(
        "doc1",
        "adaptive retrieval using rag"
    )


    result=index.search(
        "rag"
    )


    assert result[0]["id"]=="doc1"



def test_metadata_index():

    index=MetadataIndex()


    index.add(
        "doc1",
        {
            "language":"python"
        }
    )


    result=index.filter(
        {
            "language":"python"
        }
    )


    assert "doc1" in result



def test_graph_index():

    graph=GraphIndex()


    graph.add_relationship(
        "RAG",
        "uses",
        "Embedding"
    )


    result=graph.get_neighbors(
        "RAG"
    )


    assert result[0]["target"]=="Embedding"



def test_temporal_index():


    index=TemporalIndex()


    index.add(
        "doc1",
        datetime.now()
    )


    latest=index.latest()


    assert latest[0]["id"]=="doc1"



# ==========================================================
# Storage Tests
# ==========================================================


@pytest.mark.asyncio
async def test_document_storage():


    store=InMemoryDocumentStore()


    await store.initialize()


    await store.save(
        "doc1",
        "RAG system architecture",
        {
            "source":"paper"
        }
    )


    doc=await store.get(
        "doc1"
    )


    assert doc["content"]=="RAG system architecture"



@pytest.mark.asyncio
async def test_vector_storage():


    store=InMemoryVectorStore()


    await store.initialize()


    await store.add(
        "doc1",
        [
            0.1,
            0.2
        ],
        {
            "title":"RAG"
        }
    )


    result=await store.search(
        [
            0.1,
            0.2
        ]
    )


    assert result[0]["id"]=="doc1"



# ==========================================================
# Planner Tests
# ==========================================================


def test_query_analyzer():


    analyzer=QueryAnalyzer()


    result=analyzer.analyze(
        "Explain RAG architecture"
    )


    assert result.intent.primary.value=="explanation"




def test_intent_classifier():

    analyzer=QueryAnalyzer()


    result=analyzer.analyze(
        "What is vector database?"
    )


    assert result.intent.primary in [
        RetrievalIntent.DEFINITION,
        RetrievalIntent.EXPLANATION
    ]




def test_retrieval_planner():


    planner=RetrievalPlanner()


    class Complexity:

        requires_search=False
        requires_code=False
        requires_multi_hop=False



    plan=planner.create_plan(
        query="Explain RAG",
        intent="explanation",
        complexity=Complexity()
    )


    assert plan.mode.value=="vector"



# ==========================================================
# Query Model Test
# ==========================================================


def test_query_model():


    query=Query(
        text="Find RAG papers"
    )


    assert query.text=="Find RAG papers"



# ==========================================================
# Full Knowledge -> Retrieval Flow
# ==========================================================


@pytest.mark.asyncio
async def test_knowledge_to_retrieval_pipeline():


    #
    # 1. Store document
    #

    document_store=InMemoryDocumentStore()


    await document_store.initialize()


    await document_store.save(
        "doc1",
        "RAG uses embeddings and vector search",
        {
            "topic":"AI"
        }
    )


    #
    # 2. Create vector index
    #

    vector_index=VectorIndex()


    vector_index.add(
        "doc1",
        [
            1,
            0,
            0
        ],
        {
            "topic":"AI"
        }
    )


    #
    # 3. Query embedding
    #

    embedding_model=FakeEmbeddingModel()


    query_vector=await embedding_model.embed_query(
        "RAG"
    )


    #
    # 4. Retrieve
    #

    results=vector_index.search(
        query_vector
    )


    #
    # Assertions
    #

    assert results is not None

    assert len(results)==1

    assert results[0]["metadata"]["topic"]=="AI"