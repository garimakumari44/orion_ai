"""
Unit tests for Retrieval Planner.

Tests:
- Greeting routing
- Web search routing
- Code retrieval routing
- Multi-hop retrieval
- Entity lookup
- Documentation search
- Default vector retrieval
"""

import pytest

from app.adaptive_retrieval.planner.retrieval_planner import (
    RetrievalPlanner,
    RetrievalMode,
)

from app.adaptive_retrieval.planner.complexity_estimator import (
    ComplexityEstimate,
)

from app.adaptive_retrieval.planner.intent_classifier import (
    IntentClassifier,
    RetrievalIntent,
)


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture
def planner():
    return RetrievalPlanner()


@pytest.fixture
def classifier():
    return IntentClassifier()


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------


def make_complexity(
    level="simple",
    requires_search=False,
    requires_reasoning=False,
    requires_multi_hop=False,
    requires_code=False,
):

    return ComplexityEstimate(
        level=level,
        score=1,
        estimated_steps=1,
        requires_search=requires_search,
        requires_reasoning=requires_reasoning,
        requires_multi_hop=requires_multi_hop,
        requires_code=requires_code,
        explanation="test complexity",
    )


# ---------------------------------------------------------
# Greeting
# ---------------------------------------------------------


def test_greeting_returns_none_mode(planner):

    complexity = make_complexity(
        level="simple"
    )

    plan = planner.create_plan(
        query="hello",
        intent="greeting",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.NONE
    assert plan.rerank is False



# ---------------------------------------------------------
# Web Search
# ---------------------------------------------------------


def test_web_search_plan(planner):

    complexity = make_complexity(
        level="complex",
        requires_search=True,
    )

    plan = planner.create_plan(
        query="latest AI news",
        intent="temporal",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.WEB
    assert plan.top_k == 10
    assert plan.rerank is True

    assert "Web Search" in plan.retrieval_steps



# ---------------------------------------------------------
# Code Retrieval
# ---------------------------------------------------------


def test_code_query_uses_hybrid(planner):

    complexity = make_complexity(
        level="medium",
        requires_code=True,
    )

    plan = planner.create_plan(
        query="implement python authentication",
        intent="procedure",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.HYBRID
    assert plan.use_query_expansion is True
    assert plan.top_k == 15

    assert "Vector Search" in plan.retrieval_steps



# ---------------------------------------------------------
# Multi-hop Retrieval
# ---------------------------------------------------------


def test_multi_hop_query(planner):

    complexity = make_complexity(
        level="complex",
        requires_multi_hop=True,
    )

    plan = planner.create_plan(
        query=(
            "Explain relationship between "
            "OpenAI models and transformer architecture"
        ),
        intent="reasoning",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.MULTI_STAGE
    assert plan.top_k == 20

    assert "Graph Expansion" in plan.retrieval_steps



# ---------------------------------------------------------
# Entity Lookup
# ---------------------------------------------------------


def test_entity_lookup_uses_graph(planner):

    complexity = make_complexity(
        level="simple"
    )

    plan = planner.create_plan(
        query="Who is Sam Altman?",
        intent="entity_lookup",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.GRAPH
    assert plan.top_k == 10



# ---------------------------------------------------------
# Documentation
# ---------------------------------------------------------


def test_documentation_query(planner):

    complexity = make_complexity(
        level="medium"
    )

    plan = planner.create_plan(
        query="Python API documentation guide",
        intent="procedure",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.KEYWORD
    assert plan.rerank is False

    assert "Keyword Search" in plan.retrieval_steps



# ---------------------------------------------------------
# Default Vector Retrieval
# ---------------------------------------------------------


def test_default_vector_retrieval(planner):

    complexity = make_complexity(
        level="medium"
    )

    plan = planner.create_plan(
        query="Explain machine learning",
        intent="explanation",
        complexity=complexity,
    )

    assert plan.mode == RetrievalMode.VECTOR
    assert plan.top_k == 8
    assert plan.rerank is True



# ---------------------------------------------------------
# Intent Classifier Tests
# ---------------------------------------------------------


def test_intent_classifier_definition(classifier):

    result = classifier.classify(
        "What is retrieval augmented generation?"
    )

    assert (
        result.primary
        == RetrievalIntent.DEFINITION
    )

    assert result.confidence > 0



def test_intent_classifier_comparison(classifier):

    result = classifier.classify(
        "Compare BM25 vs vector search"
    )

    assert (
        result.primary
        == RetrievalIntent.COMPARISON
    )