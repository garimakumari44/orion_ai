"""
Tests for ResearchAgent.
"""

import pytest

from app.agents.base.agent_context import AgentContext
from app.agents.research.research_agent import ResearchAgent


@pytest.fixture
def agent():
    return ResearchAgent()


@pytest.fixture
def context():
    return AgentContext(
        query="Artificial Intelligence",
    )


# ---------------------------------------------------------------------
# execute()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute(agent, context):

    result = await agent.execute(context)

    assert result["agent"] == "research"

    assert result["query"] == "Artificial Intelligence"

    assert result["status"] == "completed"

    assert result["summary"] == ""

    assert result["findings"] == []

    assert result["sources"] == []

    assert result["confidence"] == 0.0

    assert result["metadata"] == {}


@pytest.mark.asyncio
async def test_execute_uses_task():

    context = AgentContext(
        query="original query",
        task="planner task",
    )

    result = await ResearchAgent().execute(context)

    assert result["query"] == "planner task"


# ---------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_success(agent):

    context = AgentContext(query="Python")

    assert await agent.validate(context)


@pytest.mark.asyncio
async def test_validate_empty(agent):

    context = AgentContext(query="")

    assert not await agent.validate(context)


# ---------------------------------------------------------------------
# plan_research()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_plan_research(agent):

    plan = await agent.plan_research("LLMs")

    assert len(plan) == 5

    assert plan[0] == "Background of LLMs"

    assert plan[-1] == "Future trends of LLMs"


# ---------------------------------------------------------------------
# organize_findings()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_organize_findings(agent):

    findings = [
        {"title": "A"},
        {"title": "B"},
    ]

    report = await agent.organize_findings(findings)

    assert report["findings"] == findings

    assert report["source_count"] == 2

    assert report["summary"] == ""


# ---------------------------------------------------------------------
# remove_duplicates()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_remove_duplicates(agent):

    findings = [
        {
            "title": "A",
            "source": "Google",
        },
        {
            "title": "A",
            "source": "Google",
        },
        {
            "title": "B",
            "source": "GitHub",
        },
        {
            "title": "B",
            "source": "GitHub",
        },
        {
            "title": "C",
            "source": "Wikipedia",
        },
    ]

    unique = await agent.remove_duplicates(findings)

    assert len(unique) == 3

    assert unique[0]["title"] == "A"

    assert unique[1]["title"] == "B"

    assert unique[2]["title"] == "C"


# ---------------------------------------------------------------------
# evaluate_sources()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_sources_empty(agent):

    confidence = await agent.evaluate_sources([])

    assert confidence == 0.0


@pytest.mark.asyncio
async def test_evaluate_sources_partial(agent):

    findings = [{"title": str(i)} for i in range(5)]

    confidence = await agent.evaluate_sources(findings)

    assert confidence == 0.5


@pytest.mark.asyncio
async def test_evaluate_sources_max(agent):

    findings = [{"title": str(i)} for i in range(20)]

    confidence = await agent.evaluate_sources(findings)

    assert confidence == 1.0


# ---------------------------------------------------------------------
# inherited BaseAgent.run()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run(agent, context):

    result = await agent.run(context)

    assert result["status"] == "completed"

    assert result["agent"] == "research"