"""
Unit tests for CriticAgent.
"""

from __future__ import annotations

import pytest

from app.agents.critic.critic_agent import CriticAgent
from app.agents.base.agent_context import AgentContext


@pytest.fixture
def agent() -> CriticAgent:
    """Return a CriticAgent instance."""
    return CriticAgent()


@pytest.fixture
def context() -> AgentContext:
    """Return a default AgentContext."""
    return AgentContext(
        query="Review this response.",
        task="Quality review",
        metadata={},
    )


# ---------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------


def test_initialization(agent: CriticAgent) -> None:
    """Agent should initialize correctly."""

    assert agent.name == "critic"
    assert agent.description == (
        "Evaluates and critiques outputs from other agents."
    )

    expected = {
        "quality_review",
        "consistency_check",
        "completeness_check",
        "feedback_generation",
        "scoring",
    }

    assert set(agent.capabilities) == expected


# ---------------------------------------------------------------------
# Capability checks
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "capability",
    [
        "quality_review",
        "consistency_check",
        "completeness_check",
        "feedback_generation",
        "scoring",
    ],
)
def test_supports_known_capabilities(
    agent: CriticAgent,
    capability: str,
) -> None:
    """supports() should return True for supported capabilities."""

    assert agent.supports(capability)


def test_supports_unknown_capability(
    agent: CriticAgent,
) -> None:
    """Unknown capability should return False."""

    assert not agent.supports("translation")


# ---------------------------------------------------------------------
# review()
# ---------------------------------------------------------------------


def test_review_empty_content(
    agent: CriticAgent,
) -> None:
    """Empty content should receive a zero score."""

    result = agent.review("")

    assert result["score"] == 0
    assert result["summary"] == "No content to review."
    assert result["issues"] == ["Empty response."]
    assert result["strengths"] == []
    assert result["suggestions"] == [
        "Generate a meaningful response."
    ]


def test_review_short_content(
    agent: CriticAgent,
) -> None:
    """Short responses should receive deductions."""

    result = agent.review("This is short.")

    assert result["score"] == 70
    assert "Response is very short." in result["issues"]
    assert "Limited amount of information." in result["issues"]

    assert (
        "Provide more detailed explanations."
        in result["suggestions"]
    )
    assert (
        "Expand important sections."
        in result["suggestions"]
    )

    assert result["summary"] == "The response can be improved."


def test_review_long_content(
    agent: CriticAgent,
) -> None:
    """Long responses should receive a high score."""

    content = " ".join(["excellent"] * 50)

    result = agent.review(content)

    assert result["score"] == 100
    assert result["issues"] == []
    assert result["suggestions"] == []
    assert result["summary"] == "The response is acceptable."

    assert "Response is readable." in result["strengths"]
    assert "Content is syntactically valid." in result["strengths"]


# ---------------------------------------------------------------------
# execute()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_with_metadata_output(
    agent: CriticAgent,
    context: AgentContext,
) -> None:
    """execute() should review metadata['output'] first."""

    context.metadata["output"] = " ".join(["good"] * 50)

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["status"] == "success"
    assert result["agent"] == "critic"
    assert result["task"] == context.task

    review = result["review"]

    assert review["score"] == 100


@pytest.mark.asyncio
async def test_execute_falls_back_to_task(
    agent: CriticAgent,
) -> None:
    """execute() should fall back to task when metadata is empty."""

    context = AgentContext(
        query="query",
        task="This is a review task.",
        metadata={},
    )

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["review"]["score"] > 0


@pytest.mark.asyncio
async def test_execute_falls_back_to_query(
    agent: CriticAgent,
) -> None:
    """execute() should use query when task is missing."""

    context = AgentContext(
        query="Only query available.",
        task="",
        metadata={},
    )

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["task"] == "Only query available."


# ---------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_accepts_dict(
    agent: CriticAgent,
) -> None:
    """validate() should accept dictionaries."""

    assert await agent.validate({}) is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    [
        [],
        "",
        None,
        123,
        3.14,
        object(),
    ],
)
async def test_validate_rejects_non_dict(
    agent: CriticAgent,
    value,
) -> None:
    """validate() should reject non-dictionaries."""

    assert await agent.validate(value) is False


# ---------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run(
    agent: CriticAgent,
    context: AgentContext,
) -> None:
    """run() should delegate to execute()."""

    context.metadata["output"] = " ".join(["quality"] * 50)

    result = await agent.run(context)

    assert result["success"] is True
    assert result["agent"] == "critic"
    assert "review" in result