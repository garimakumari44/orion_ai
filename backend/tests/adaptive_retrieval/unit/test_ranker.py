"""
Unit tests for ranking algorithms.

Tests:
- Token overlap scoring
- Document text extraction
- Result reranking
- Top-k selection
- RankedDocument output
"""

import pytest

from app.adaptive_retrieval.ranking.ranker import (
    TokenOverlapRanker,
)

from app.adaptive_retrieval.ranking.reranker import (
    ResultReranker,
    RankedDocument,
)


# ============================================================
# TokenOverlapRanker Tests
# ============================================================


def test_token_overlap_full_match():
    """
    Query tokens completely exist in document.
    """

    ranker = TokenOverlapRanker()

    document = {
        "text": "python machine learning retrieval system"
    }

    score = ranker.score(
        "python machine learning",
        document,
    )

    assert score == 1.0



def test_token_overlap_partial_match():
    """
    Only some query tokens match.
    """

    ranker = TokenOverlapRanker()

    document = {
        "text": "python programming language"
    }

    score = ranker.score(
        "python machine learning",
        document,
    )

    assert score == pytest.approx(
        1 / 3
    )



def test_token_overlap_no_match():
    """
    No query tokens appear.
    """

    ranker = TokenOverlapRanker()

    document = {
        "text": "database indexing storage"
    }


    score = ranker.score(
        "python machine learning",
        document,
    )


    assert score == 0.0



def test_token_overlap_empty_document():

    ranker = TokenOverlapRanker()

    document = {
        "text": ""
    }


    score = ranker.score(
        "python",
        document,
    )


    assert score == 0.0



def test_token_overlap_object_document():

    class MockChunk:

        def __init__(self):
            self.text = (
                "adaptive retrieval system"
            )


    ranker = TokenOverlapRanker()


    score = ranker.score(
        "adaptive retrieval",
        MockChunk(),
    )


    assert score == 1.0



# ============================================================
# ResultReranker Tests
# ============================================================


def test_reranker_scores_documents():

    reranker = ResultReranker()


    documents = [

        {
            "text":
            "python machine learning"
        },

        {
            "text":
            "database systems"
        },

    ]


    results = reranker.rerank(
        "python learning",
        documents,
    )


    assert len(results) == 2

    assert isinstance(
        results[0],
        RankedDocument
    )



def test_reranker_orders_by_score():

    reranker = ResultReranker()


    documents = [

        {
            "text":
            "database indexing"
        },

        {
            "text":
            "python machine learning system"
        },

        {
            "text":
            "python"
        },

    ]


    results = reranker.rerank(
        "python machine learning",
        documents,
    )


    assert results[0].score >= results[1].score

    assert (
        results[0].document["text"]
        ==
        "python machine learning system"
    )



def test_reranker_top_k():

    reranker = ResultReranker(
        top_k=2
    )


    documents = [

        {
            "text":
            "python machine learning"
        },

        {
            "text":
            "python"
        },

        {
            "text":
            "database"
        },

    ]


    results = reranker.rerank(
        "python",
        documents,
    )


    assert len(results) == 2



def test_reranker_empty_input():

    reranker = ResultReranker()


    results = reranker.rerank(
        "python",
        [],
    )


    assert results == []



def test_reranker_handles_missing_text():

    reranker = ResultReranker()


    documents = [

        {
            "content":
            "python code"
        },

        {
            "unknown":
            "value"
        },

    ]


    results = reranker.rerank(
        "python",
        documents,
    )


    assert results[0].score == 1.0

    assert results[1].score == 0.0