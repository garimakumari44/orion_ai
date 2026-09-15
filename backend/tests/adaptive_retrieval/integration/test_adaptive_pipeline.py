"""
Integration tests for the Adaptive Retrieval Pipeline.

Pipeline:

Query
  ↓
Rewrite
  ↓
Expand
  ↓
Analyze
  ↓
Intent
  ↓
Complexity
  ↓
Planner
  ↓
Retrieval
  ↓
Deduplication
  ↓
Reranking
  ↓
Compression
  ↓
Context Builder
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.adaptive_retrieval.rewriting.query_rewriter import (
    QueryRewriter,
    QueryRewriteRequest,
)
from app.adaptive_retrieval.rewriting.expansion import (
    QueryExpander,
    ExpansionRequest,
)
from app.adaptive_retrieval.planner.query_analyzer import (
    QueryAnalyzer,
)
from app.adaptive_retrieval.planner.intent_classifier import (
    RetrievalIntent,
)
from app.adaptive_retrieval.planner.complexity_estimator import (
    ComplexityEstimator,
)
from app.adaptive_retrieval.planner.retrieval_planner import (
    RetrievalPlanner,
    RetrievalMode,
)
from app.adaptive_retrieval.ranking.deduplication import (
    Deduplicator,
)
from app.adaptive_retrieval.ranking.reranker import (
    ResultReranker,
)
from app.adaptive_retrieval.compression.contextual import (
    ContextualCompressor,
)
from app.adaptive_retrieval.context.builder import (
    ContextBuilder,
)


# ============================================================
# Fake Chunk
# ============================================================

_SHARED_DOC = uuid4()


class FakeChunk:
    """
    Lightweight Chunk replacement used for testing.
    """

    def __init__(
        self,
        text: str,
        score: float = 1.0,
        document_id=None,
    ):
        self.id = uuid4()
        self.document_id = document_id or uuid4()
        self.text = text
        self.score = score


# ============================================================
# Fake Retrieval Manager
# ============================================================


class FakeRetrievalManager:
    """
    Simulates retrieval results.
    """

    def retrieve(
        self,
        query,
        **kwargs,
    ):

        return [

            FakeChunk(
                "Python FastAPI tutorial",
                score=0.95,
                document_id=_SHARED_DOC,
            ),

            FakeChunk(
                "FastAPI API guide",
                score=0.90,
            ),

            FakeChunk(
                "Python FastAPI tutorial",
                score=0.95,
                document_id=_SHARED_DOC,
            ),
        ]


# ============================================================
# Full Pipeline
# ============================================================


def test_complete_adaptive_pipeline():

    query = (
        "Please explain how to build a FastAPI API"
    )

    # --------------------------------------------------------
    # Rewrite
    # --------------------------------------------------------

    rewritten = QueryRewriter().rewrite(
        QueryRewriteRequest(query=query)
    )

    assert rewritten.original_query == query
    assert rewritten.rewritten_query
    assert rewritten.variants

    # --------------------------------------------------------
    # Expansion
    # --------------------------------------------------------

    expanded = QueryExpander().expand(
        ExpansionRequest(
            query=rewritten.rewritten_query
        )
    )

    assert expanded.expanded_query
    assert isinstance(
        expanded.expansion_terms,
        list,
    )

    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    analysis = QueryAnalyzer().analyze(
        expanded.expanded_query
    )

    assert analysis.original_query
    assert analysis.tokens

    assert analysis.intent.primary in (
        RetrievalIntent.PROCEDURE,
        RetrievalIntent.EXPLANATION,
        RetrievalIntent.UNKNOWN,
    )

    # --------------------------------------------------------
    # Complexity
    # --------------------------------------------------------

    complexity = ComplexityEstimator().estimate(
        expanded.expanded_query
    )

    assert complexity.score >= 0
    assert complexity.level is not None
    assert complexity.estimated_steps >= 1

    # --------------------------------------------------------
    # Planner
    # --------------------------------------------------------

    planner = RetrievalPlanner()

    plan = planner.create_plan(
        expanded.expanded_query,
        analysis.intent.primary.value,
        complexity,
    )

    assert plan.top_k > 0
    assert len(plan.retrieval_steps) > 0

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    manager = FakeRetrievalManager()

    retrieved = manager.retrieve(
        expanded.expanded_query,
        top_k=plan.top_k,
    )

    assert len(retrieved) == 3

    # --------------------------------------------------------
    # Deduplication
    # --------------------------------------------------------

    deduplicator = Deduplicator()

    unique = deduplicator.deduplicate(
        retrieved
    )

    assert len(unique) == 2

    # --------------------------------------------------------
    # Reranking
    # --------------------------------------------------------

    reranker = ResultReranker(
        top_k=5
    )

    ranked = reranker.rerank(
        expanded.expanded_query,
        unique,
    )

    assert len(ranked) == 2

    assert ranked[0].score >= ranked[1].score

    # --------------------------------------------------------
    # Compression
    # --------------------------------------------------------

    compressor = ContextualCompressor()

    compressed = compressor.compress(
        expanded.expanded_query,
        [r.document for r in ranked],
    )

    assert len(compressed) > 0

    # --------------------------------------------------------
    # Context Building
    # --------------------------------------------------------

    docs = [
        {
            "text": chunk.text,
        }
        for chunk in compressed
    ]

    context = ContextBuilder().build(
        docs
    )

    assert isinstance(
        context,
        str,
    )

    assert "FastAPI" in context


# ============================================================
# Memory Retriever
# ============================================================


def test_memory_reuse():

    from app.adaptive_retrieval.retrievers.memory import (
        MemoryRetriever,
    )

    memory = MemoryRetriever()

    chunks = [
        FakeChunk(
            "Machine learning",
        )
    ]

    memory.add(
        "ml",
        chunks,
    )

    cached = memory.retrieve(
        "ml"
    )

    assert cached == chunks

    assert memory.size == 1


def test_memory_clear():

    from app.adaptive_retrieval.retrievers.memory import (
        MemoryRetriever,
    )

    memory = MemoryRetriever()

    memory.add(
        "python",
        [FakeChunk("Python")],
    )

    assert memory.size == 1

    memory.clear()

    assert memory.size == 0


# ============================================================
# Planner Routing
# ============================================================


@pytest.mark.parametrize(
    "query,expected",
    [
        (
            "latest AI news",
            RetrievalMode.WEB,
        ),
        (
            "build FastAPI application",
            RetrievalMode.HYBRID,
        ),
        (
            "who is OpenAI",
            RetrievalMode.GRAPH,
        ),
    ],
)
def test_pipeline_planner_routes(
    query,
    expected,
):

    complexity = ComplexityEstimator().estimate(
        query
    )

    analysis = QueryAnalyzer().analyze(
        query
    )

    plan = RetrievalPlanner().create_plan(
        query,
        analysis.intent.primary.value,
        complexity,
    )

    assert plan.mode == expected