import pytest
from unittest.mock import AsyncMock, MagicMock

from app.adaptive_retrieval.rewriting.query_rewriter import (
    QueryRewriter,
    QueryRewriteRequest,
)

from app.adaptive_retrieval.planner.query_analyzer import QueryAnalyzer
from app.adaptive_retrieval.planner.retrieval_planner import (
    RetrievalPlanner,
)

from app.adaptive_retrieval.ranking.reranker import ResultReranker
from app.adaptive_retrieval.compression.contextual import (
    ContextualCompressor,
)
from app.adaptive_retrieval.context.builder import ContextBuilder


# -------------------------------------------------------------------
# Fake Chunk
# -------------------------------------------------------------------

class FakeChunk:

    def __init__(self, idx, text):

        self.id = idx
        self.text = text
        self.content = text
        self.score = 0.9
        self.metadata = {
            "source": "unit-test"
        }


# -------------------------------------------------------------------
# Pipeline
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rag_pipeline():

    query = "Explain RAG architecture"

    # -------------------------------------------------------
    # Rewrite
    # -------------------------------------------------------

    rewriter = QueryRewriter()

    rewritten = rewriter.rewrite(
        QueryRewriteRequest(query=query)
    )

    assert rewritten.rewritten_query != ""

    # -------------------------------------------------------
    # Analyze
    # -------------------------------------------------------

    analyzer = QueryAnalyzer()

    analysis = analyzer.analyze(
        rewritten.rewritten_query
    )

    assert analysis.tokens
    assert analysis.intent is not None

    # -------------------------------------------------------
    # Plan
    # -------------------------------------------------------

    planner = RetrievalPlanner()

    complexity = MagicMock()

    complexity.requires_search = False
    complexity.requires_code = False
    complexity.requires_multi_hop = False

    plan = planner.create_plan(
        query=rewritten.rewritten_query,
        intent=analysis.intent.primary.value,
        complexity=complexity,
    )

    assert plan.mode is not None

    # -------------------------------------------------------
    # Retrieval (mock)
    # -------------------------------------------------------

    retrieved = [
        FakeChunk(
            1,
            "Retrieval Augmented Generation combines retrieval with LLMs."
        ),
        FakeChunk(
            2,
            "Vector databases store embeddings."
        ),
    ]

    assert len(retrieved) == 2

    # -------------------------------------------------------
    # Rerank
    # -------------------------------------------------------

    reranker = ResultReranker(
        top_k=2
    )

    ranked = reranker.rerank(
        query,
        retrieved,
    )

    assert len(ranked) == 2
    assert ranked[0].score >= ranked[1].score

    # -------------------------------------------------------
    # Compression
    # -------------------------------------------------------

    compressor = ContextualCompressor()

    compressed = compressor.compress(
        query,
        [r.document for r in ranked],
    )

    assert len(compressed) > 0

    # -------------------------------------------------------
    # Build Context
    # -------------------------------------------------------

    builder = ContextBuilder()

    documents = [
        {
            "text": c.text,
            "source": c.metadata["source"],
        }
        for c in compressed
    ]

    context = builder.build(
        documents
    )

    assert isinstance(context, str)
    assert len(context) > 0

    assert "retrieval" in context.lower()