import pytest

from app.agents.news.news_agent import NewsAgent
from app.agents.base.agent_context import AgentContext


# ==========================================================
# Fake News Tool
# ==========================================================

class FakeNewsTool:
    async def search(self, query: str):
        return [
            {
                "title": "OpenAI launches GPT",
                "source": "Example News",
                "query": query,
            }
        ]


class FailingNewsTool:
    async def search(self, query: str):
        raise RuntimeError("News provider unavailable")


# ==========================================================
# Fake Tool Registry
# ==========================================================

class FakeToolRegistry(dict):
    """
    Minimal registry used for unit testing.
    """
    pass


# ==========================================================
# execute() success
# ==========================================================

@pytest.mark.asyncio
async def test_news_agent_execute_success():

    registry = FakeToolRegistry()
    registry["news"] = FakeNewsTool()

    context = AgentContext(
        query="AI",
        task="Latest AI news",
    )

    context.tool_registry = registry

    agent = NewsAgent()

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["agent"] == "news"
    assert result["task"] == "Latest AI news"

    assert len(result["results"]) == 1

    assert result["results"][0]["title"] == "OpenAI launches GPT"


# ==========================================================
# execute() uses query when task is None
# ==========================================================

@pytest.mark.asyncio
async def test_news_agent_uses_query_when_task_missing():

    registry = FakeToolRegistry()
    registry["news"] = FakeNewsTool()

    context = AgentContext(
        query="Artificial Intelligence",
        task=None,
    )

    context.tool_registry = registry

    agent = NewsAgent()

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["task"] == "Artificial Intelligence"


# ==========================================================
# execute() with no registered tool
# ==========================================================

@pytest.mark.asyncio
async def test_news_agent_no_news_tool():

    context = AgentContext(
        query="AI",
        task="Latest AI news",
    )

    context.tool_registry = FakeToolRegistry()

    agent = NewsAgent()

    result = await agent.execute(context)

    assert result["success"] is False
    assert result["results"] == []

    assert result["error"] == "No news tool is registered."


# ==========================================================
# execute() provider failure
# ==========================================================

@pytest.mark.asyncio
async def test_news_agent_provider_failure():

    registry = FakeToolRegistry()
    registry["news"] = FailingNewsTool()

    context = AgentContext(
        query="AI",
        task="Latest AI news",
    )

    context.tool_registry = registry

    agent = NewsAgent()

    result = await agent.execute(context)

    assert result["success"] is False
    assert "News provider unavailable" in result["error"]
    assert result["results"] == []


# ==========================================================
# health_check() success
# ==========================================================

@pytest.mark.asyncio
async def test_news_agent_health_check_success():

    registry = FakeToolRegistry()
    registry["news"] = FakeNewsTool()

    context = AgentContext(query="AI")
    context.tool_registry = registry

    agent = NewsAgent()

    assert await agent.health_check(context) is True


# ==========================================================
# health_check() failure
# ==========================================================

@pytest.mark.asyncio
async def test_news_agent_health_check_failure():

    context = AgentContext(query="AI")
    context.tool_registry = FakeToolRegistry()

    agent = NewsAgent()

    assert await agent.health_check(context) is False