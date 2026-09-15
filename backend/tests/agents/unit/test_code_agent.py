"""
Unit tests for CodeAgent.
"""

from __future__ import annotations

import pytest

from app.agents.base.agent_context import AgentContext
from app.agents.code.code_agent import CodeAgent


@pytest.fixture
def agent() -> CodeAgent:
    """Create a CodeAgent instance."""
    return CodeAgent()


@pytest.fixture
def context() -> AgentContext:
    """Create a basic AgentContext."""
    return AgentContext(
        query="Write a Python function",
        task="Write a Python function",
        metadata={},
    )


# ---------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------


def test_code_agent_initialization(agent: CodeAgent) -> None:
    """Verify CodeAgent initializes correctly."""

    assert agent.name == "code"

    assert "code" in agent.description.lower()

    assert len(agent.capabilities) == 7

    assert agent.supports("code_generation")
    assert agent.supports("bug_fixing")
    assert agent.supports("code_review")
    assert agent.supports("refactoring")
    assert agent.supports("documentation")
    assert agent.supports("test_generation")
    assert agent.supports("code_explanation")


def test_supports_unknown_capability(agent: CodeAgent) -> None:
    """Unsupported capabilities should return False."""

    assert not agent.supports("database_design")
    assert not agent.supports("machine_learning")


# ---------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_returns_expected_structure(
    agent: CodeAgent,
    context: AgentContext,
) -> None:
    """execute() should return the expected response."""

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["agent"] == "code"
    assert result["task"] == context.task
    assert result["status"] == "pending_tool_execution"

    assert "placeholder" in result["output"].lower()

    assert result["metadata"]["capabilities"] == agent.capabilities


@pytest.mark.asyncio
async def test_execute_uses_query_when_task_missing(
    agent: CodeAgent,
    context: AgentContext,
) -> None:
    """If task is empty, query should be used."""

    context.task = ""
    context.query = "Explain decorators"

    result = await agent.execute(context)

    assert result["task"] == "Explain decorators"


@pytest.mark.asyncio
async def test_execute_with_empty_context(
    agent: CodeAgent,
    context: AgentContext,
) -> None:
    """Agent should handle empty task/query."""

    context.task = ""
    context.query = ""

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["task"] == ""
    assert result["status"] == "pending_tool_execution"


# ---------------------------------------------------------------------
# Integration with BaseAgent.run()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_calls_execute(
    agent: CodeAgent,
    context: AgentContext,
) -> None:
    """BaseAgent.run() should delegate to execute()."""

    result = await agent.run(context)

    assert result["success"] is True
    assert result["agent"] == "code"
    assert result["task"] == context.task
    assert result["status"] == "pending_tool_execution"