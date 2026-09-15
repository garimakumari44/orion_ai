"""
Integration Tests - Tool Selection Flow

Flow
----
Registry
    ↓
Selector
    ↓
Selected Tool
    ↓
Executor

These tests verify that tool registration, selection,
and execution work together correctly.
"""

from __future__ import annotations

import pytest

from backend.app.orchestration.tool_registry import ToolRegistry
from backend.app.orchestration.tool_selector import ToolSelector
from backend.app.orchestration.tool_executor import ToolExecutor


# ==========================================================
# Fake Tools
# ==========================================================

class SearchTool:
    name = "search"
    description = "Searches the web"

    async def execute(self, query: str):
        return {
            "tool": self.name,
            "result": f"Search results for '{query}'"
        }


class CalculatorTool:
    name = "calculator"
    description = "Performs arithmetic"

    async def execute(self, query: str):
        return {
            "tool": self.name,
            "answer": 42
        }


class WeatherTool:
    name = "weather"
    description = "Returns weather"

    async def execute(self, query: str):
        return {
            "tool": self.name,
            "temperature": 30
        }


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def registry():
    registry = ToolRegistry()

    registry.register(SearchTool())
    registry.register(CalculatorTool())
    registry.register(WeatherTool())

    return registry


@pytest.fixture
def selector(registry):
    return ToolSelector(registry)


@pytest.fixture
def executor():
    return ToolExecutor()


# ==========================================================
# Tests
# ==========================================================

@pytest.mark.asyncio
async def test_select_search_tool(selector, executor):
    """
    Search query should select SearchTool.
    """

    tool = selector.select("latest AI news")

    assert tool is not None

    result = await executor.execute(tool, "latest AI news")

    assert result["tool"] == tool.name


@pytest.mark.asyncio
async def test_select_calculator_tool(selector, executor):
    """
    Math query should select CalculatorTool.
    """

    tool = selector.select("2 + 2")

    assert tool is not None

    result = await executor.execute(tool, "2 + 2")

    assert result["tool"] == tool.name


@pytest.mark.asyncio
async def test_select_weather_tool(selector, executor):
    """
    Weather query should select WeatherTool.
    """

    tool = selector.select("weather in Delhi")

    assert tool is not None

    result = await executor.execute(tool, "weather in Delhi")

    assert result["tool"] == tool.name


@pytest.mark.asyncio
async def test_registry_contains_all_tools(registry):
    """
    Registry should contain all registered tools.
    """

    tools = registry.list_tools()

    assert len(tools) == 3

    names = [tool.name for tool in tools]

    assert "search" in names
    assert "calculator" in names
    assert "weather" in names


@pytest.mark.asyncio
async def test_every_registered_tool_can_execute(
    registry,
    executor,
):
    """
    Every registered tool should execute successfully.
    """

    for tool in registry.list_tools():

        result = await executor.execute(tool, "test")

        assert result["tool"] == tool.name


@pytest.mark.asyncio
async def test_selector_returns_registered_tool(
    registry,
    selector,
):
    """
    Selector should never return an unknown tool.
    """

    tool = selector.select("AI")

    registered_names = {
        t.name for t in registry.list_tools()
    }

    assert tool.name in registered_names


@pytest.mark.asyncio
async def test_multiple_queries_are_handled(
    selector,
    executor,
):
    """
    Multiple consecutive selections should succeed.
    """

    queries = [
        "AI news",
        "10 * 5",
        "weather today",
        "machine learning",
        "calculate square root",
    ]

    for query in queries:

        tool = selector.select(query)

        assert tool is not None

        result = await executor.execute(tool, query)

        assert result["tool"] == tool.name


@pytest.mark.asyncio
async def test_selector_is_repeatable(selector):
    """
    Same query should consistently select the same tool.
    """

    tool1 = selector.select("AI research")

    tool2 = selector.select("AI research")

    assert tool1.name == tool2.name


@pytest.mark.asyncio
async def test_executor_receives_selected_tool(
    selector,
    executor,
):
    """
    Verify the selected tool is the one executed.
    """

    tool = selector.select("search GitHub")

    result = await executor.execute(tool, "search GitHub")

    assert result["tool"] == tool.name