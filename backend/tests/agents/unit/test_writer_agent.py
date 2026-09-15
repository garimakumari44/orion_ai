"""
Unit tests for WriterAgent.
"""

from __future__ import annotations

import pytest

from app.agents.base.agent_context import AgentContext
from app.agents.writer.writer_agent import WriterAgent


@pytest.fixture
def agent() -> WriterAgent:
    """Create a WriterAgent instance."""
    return WriterAgent()


@pytest.fixture
def context() -> AgentContext:
    """Create a default AgentContext."""
    return AgentContext(
        query="Generate a project report",
        task="Create final documentation",
        metadata={},
    )


def test_writer_agent_initialization(agent: WriterAgent) -> None:
    """WriterAgent initializes correctly."""

    assert agent.name == "writer"
    assert agent.description == "Generates polished reports and final responses."

    assert agent.supports("write")
    assert agent.supports("summarize")
    assert agent.supports("report")
    assert agent.supports("markdown")
    assert agent.supports("documentation")

    assert not agent.supports("search")
    assert not agent.supports("github")


@pytest.mark.asyncio
async def test_execute_with_all_sections(
    agent: WriterAgent,
    context: AgentContext,
) -> None:
    """WriterAgent should include every report section."""

    context.metadata = {
        "synthesized_result": "Overall system is functioning correctly.",
        "research": "Research indicates improved performance.",
        "code": "print('Hello World')",
    }

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["agent"] == "writer"
    assert result["task"] == "Create final documentation"

    report = result["result"]

    assert "# Final Report" in report
    assert "## Task" in report
    assert "Create final documentation" in report

    assert "## Summary" in report
    assert "Overall system is functioning correctly." in report

    assert "## Research Findings" in report
    assert "Research indicates improved performance." in report

    assert "## Code" in report
    assert "print('Hello World')" in report
    assert "```" in report


@pytest.mark.asyncio
async def test_execute_with_empty_metadata(
    agent: WriterAgent,
    context: AgentContext,
) -> None:
    """WriterAgent should generate a minimal report."""

    result = await agent.execute(context)

    report = result["result"]

    assert result["success"] is True

    assert "# Final Report" in report
    assert "## Task" in report
    assert "Create final documentation" in report

    assert "## Summary" not in report
    assert "## Research Findings" not in report
    assert "## Code" not in report


@pytest.mark.asyncio
async def test_execute_uses_query_when_task_missing(
    agent: WriterAgent,
) -> None:
    """WriterAgent should fall back to query when task is empty."""

    context = AgentContext(
        query="Summarize AI research",
        task="",
        metadata={},
    )

    result = await agent.execute(context)

    assert result["task"] == "Summarize AI research"
    assert "Summarize AI research" in result["result"]


def test_build_report_all_sections(agent: WriterAgent) -> None:
    """_build_report should include all provided sections."""

    report = agent._build_report(
        task="Build documentation",
        synthesized="Summary text",
        research="Research text",
        code="x = 1",
    )

    assert "# Final Report" in report
    assert "## Task" in report
    assert "Build documentation" in report

    assert "## Summary" in report
    assert "Summary text" in report

    assert "## Research Findings" in report
    assert "Research text" in report

    assert "## Code" in report
    assert "x = 1" in report


def test_build_report_task_only(agent: WriterAgent) -> None:
    """_build_report should omit empty sections."""

    report = agent._build_report(
        task="Simple task",
        synthesized="",
        research="",
        code="",
    )

    assert "# Final Report" in report
    assert "Simple task" in report

    assert "## Summary" not in report
    assert "## Research Findings" not in report
    assert "## Code" not in report