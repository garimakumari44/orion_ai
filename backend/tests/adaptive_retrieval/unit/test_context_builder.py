"""
Unit tests for Context Builder and Contextual Compressor.

Tests:
- Context construction
- Token limit handling
- Metadata preservation
- Empty input handling
- Chunk compression
- Query overlap scoring
"""

import pytest

from app.adaptive_retrieval.context.builder import (
    ContextBuilder,
)

from app.adaptive_retrieval.compression.contextual import (
    ContextualCompressor,
)

from app.knowledge_system.models.chunk import Chunk



# ============================================================
# Context Builder Tests
# ============================================================


def test_context_builder_combines_documents():
    """
    Documents should be combined
    into a single context string.
    """

    builder = ContextBuilder()

    documents = [
        {
            "text": "First document content",
            "source": "doc1"
        },
        {
            "text": "Second document content",
            "source": "doc2"
        }
    ]

    result = builder.build(
        documents
    )

    assert (
        result
        ==
        "First document content\n\nSecond document content"
    )



def test_context_builder_empty_documents():
    """
    Empty document list should
    return empty context.
    """

    builder = ContextBuilder()

    result = builder.build([])

    assert result == ""



def test_context_builder_missing_text():
    """
    Documents without text
    should be ignored safely.
    """

    builder = ContextBuilder()

    documents = [
        {
            "source": "missing_text"
        },
        {
            "text": "valid content"
        }
    ]

    result = builder.build(
        documents
    )

    assert result == "valid content"



def test_context_builder_respects_token_limit():
    """
    Context should stop adding documents
    after max token limit.
    """

    builder = ContextBuilder(
        max_tokens=5
    )

    documents = [
        {
            "text": "one two three",
            "source": "doc1"
        },
        {
            "text": "four five six seven",
            "source": "doc2"
        }
    ]

    result = builder.build(
        documents
    )

    assert (
        result
        ==
        "one two three"
    )



def test_context_builder_with_metadata():
    """
    build_with_metadata should return
    context and sources.
    """

    builder = ContextBuilder()

    documents = [
        {
            "text": "AI research paper",
            "source": "paper.pdf"
        },
        {
            "text": "ML notes",
            "source": "notes.md"
        }
    ]

    result = builder.build_with_metadata(
        documents
    )

    assert result["context"] == (
        "AI research paper\n\nML notes"
    )

    assert result["sources"] == [
        "paper.pdf",
        "notes.md"
    ]



# ============================================================
# Context Compressor Tests
# ============================================================


def create_chunk(
    text,
    score=0.5
):
    """
    Helper for creating chunks.
    """

    return Chunk(
        document_id="00000000-0000-0000-0000-000000000001",
        text=text,
        chunk_index=0,
    ).model_copy(
        update={
            "score": score
        }
    )



def test_compressor_keeps_relevant_chunks():
    """
    Chunks containing query terms
    should survive compression.
    """

    compressor = ContextualCompressor(
        min_score=0.15
    )

    chunks = [
        create_chunk(
            "Python machine learning models",
            score=0.8
        ),
        create_chunk(
            "Cooking recipes and food",
            score=0.1
        )
    ]


    result = compressor.compress(
        "Python machine learning",
        chunks
    )


    assert len(result) == 1

    assert (
        result[0].text
        ==
        "Python machine learning models"
    )



def test_compressor_removes_low_score_chunks():
    """
    Irrelevant chunks should be removed.
    """

    compressor = ContextualCompressor(
        min_score=1.0
    )

    chunks = [
        create_chunk(
            "Random information",
            score=0.1
        )
    ]


    result = compressor.compress(
        "AI",
        chunks
    )


    assert result == []



def test_compressor_handles_missing_score():
    """
    Missing score should use
    default retrieval score.
    """

    compressor = ContextualCompressor()

    chunk = Chunk(
        document_id="00000000-0000-0000-0000-000000000001",
        text="Artificial intelligence systems",
        chunk_index=0,
    )


    result = compressor.compress(
        "Artificial intelligence",
        [
            chunk
        ]
    )


    assert len(result) == 1



def test_compressor_query_overlap():
    """
    More query overlap should
    increase score.
    """

    compressor = ContextualCompressor(
        min_score=0.5
    )


    chunks = [
        create_chunk(
            "retrieval augmented generation system",
            score=0.5
        ),
        create_chunk(
            "database indexing",
            score=0.5
        )
    ]


    result = compressor.compress(
        "retrieval generation",
        chunks
    )


    assert len(result) == 1

    assert (
        result[0].text
        ==
        "retrieval augmented generation system"
    )