"""
Unit tests for QueryRewriter.
"""
from app.adaptive_retrieval.rewriting.query_rewriter  import (
    QueryRewriter,
    QueryRewriteRequest,
    QueryRewriteResult,
)




# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


def test_query_rewriter_initialization():
    """
    Ensure the rewriter can be instantiated.
    """
    rewriter = QueryRewriter()

    assert isinstance(rewriter, QueryRewriter)


# ---------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------


def test_query_rewrite_request_defaults():
    request = QueryRewriteRequest(query="What is AI?")

    assert request.query == "What is AI?"
    assert request.enable_cleanup is True
    assert request.enable_expansion is True
    assert request.generate_variants is True


def test_query_rewrite_result_defaults():
    result = QueryRewriteResult(
        original_query="AI",
        rewritten_query="artificial intelligence",
    )

    assert result.original_query == "AI"
    assert result.rewritten_query == "artificial intelligence"
    assert result.variants == []


# ---------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------


def test_cleanup_removes_stop_words():
    rewriter = QueryRewriter()

    cleaned = rewriter._cleanup(
        "Please tell me about AI"
    )

    assert cleaned == "AI"


def test_cleanup_preserves_non_stop_words():
    rewriter = QueryRewriter()

    cleaned = rewriter._cleanup(
        "machine learning basics"
    )

    assert cleaned == "machine learning basics"


def test_cleanup_handles_multiple_spaces():
    rewriter = QueryRewriter()

    cleaned = rewriter._cleanup(
        "please      tell      me      AI"
    )

    assert cleaned == "AI"


def test_cleanup_empty_string():
    rewriter = QueryRewriter()

    assert rewriter._cleanup("") == ""


# ---------------------------------------------------------------------
# Expansion
# ---------------------------------------------------------------------


def test_expand_ai():
    rewriter = QueryRewriter()

    expanded = rewriter._expand("AI")

    assert expanded == "artificial intelligence"


def test_expand_multiple_abbreviations():
    rewriter = QueryRewriter()

    expanded = rewriter._expand(
        "AI ML NLP"
    )

    assert expanded == (
        "artificial intelligence "
        "machine learning "
        "natural language processing"
    )


def test_expand_unknown_word():
    rewriter = QueryRewriter()

    expanded = rewriter._expand("python")

    assert expanded == "python"


def test_expand_mixed_words():
    rewriter = QueryRewriter()

    expanded = rewriter._expand(
        "AI systems"
    )

    assert expanded == (
        "artificial intelligence systems"
    )


# ---------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------


def test_variants_generation():
    rewriter = QueryRewriter()

    variants = rewriter._variants(
        "Large Language Model"
    )

    assert "Large Language Model" in variants
    assert "large language model" in variants
    assert len(variants) >= 2


def test_variants_replace_hyphen():
    rewriter = QueryRewriter()

    variants = rewriter._variants(
        "large-language-model"
    )

    assert "large language model" in variants


def test_variants_unique():
    rewriter = QueryRewriter()

    variants = rewriter._variants(
        "hello"
    )

    assert len(variants) == len(set(variants))


# ---------------------------------------------------------------------
# Rewrite
# ---------------------------------------------------------------------


def test_rewrite_full_pipeline():
    rewriter = QueryRewriter()

    request = QueryRewriteRequest(
        query="Please tell me about AI"
    )

    result = rewriter.rewrite(request)

    assert isinstance(result, QueryRewriteResult)

    assert result.original_query == "Please tell me about AI"

    assert (
        result.rewritten_query
        == "artificial intelligence"
    )

    assert len(result.variants) > 0


def test_rewrite_without_cleanup():
    rewriter = QueryRewriter()

    request = QueryRewriteRequest(
        query="Please AI",
        enable_cleanup=False,
    )

    result = rewriter.rewrite(request)

    assert (
        result.rewritten_query
        == "Please artificial intelligence"
    )


def test_rewrite_without_expansion():
    rewriter = QueryRewriter()

    request = QueryRewriteRequest(
        query="AI",
        enable_expansion=False,
    )

    result = rewriter.rewrite(request)

    assert result.rewritten_query == "AI"


def test_rewrite_without_variants():
    rewriter = QueryRewriter()

    request = QueryRewriteRequest(
        query="AI",
        generate_variants=False,
    )

    result = rewriter.rewrite(request)

    assert result.variants == []


def test_rewrite_all_features_disabled():
    rewriter = QueryRewriter()

    request = QueryRewriteRequest(
        query=" Please AI ",
        enable_cleanup=False,
        enable_expansion=False,
        generate_variants=False,
    )

    result = rewriter.rewrite(request)

    assert result.rewritten_query == "Please AI"
    assert result.variants == []


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


def test_empty_query():
    rewriter = QueryRewriter()

    result = rewriter.rewrite(
        QueryRewriteRequest(query="")
    )

    assert result.original_query == ""
    assert result.rewritten_query == ""
    assert result.variants == [""]


def test_whitespace_query():
    rewriter = QueryRewriter()

    result = rewriter.rewrite(
        QueryRewriteRequest(query="     ")
    )

    assert result.rewritten_query == ""
    assert result.variants == [""]


def test_case_insensitive_expansion():
    rewriter = QueryRewriter()

    result = rewriter.rewrite(
        QueryRewriteRequest(query="LlM")
    )

    assert (
        result.rewritten_query
        == "large language model"
    )


def test_cpu_gpu_expansion():
    rewriter = QueryRewriter()

    result = rewriter.rewrite(
        QueryRewriteRequest(
            query="CPU GPU"
        )
    )

    assert (
        result.rewritten_query
        == "central processing unit graphics processing unit"
    )


def test_rewrite_keeps_original_query():
    rewriter = QueryRewriter()

    original = "Please AI"

    result = rewriter.rewrite(
        QueryRewriteRequest(query=original)
    )

    assert result.original_query == original