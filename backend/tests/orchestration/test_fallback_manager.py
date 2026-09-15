"""
tests/orchestration/test_fallback_manager.py
"""

from app.orchestration.fallback_manager import FallbackManager
from app.orchestration.tool_registry import ToolRegistry
from app.orchestration.capability import Capability


# ---------------------------------------------------------------------
# Fake Tool
# ---------------------------------------------------------------------

class FakeTool:
    def __init__(
        self,
        name,
        capabilities,
        available=True,
    ):
        self.name = name
        self.capabilities = capabilities
        self.available = available

    def supports(self, capability):
        return capability in self.capabilities

    def is_available(self):
        return self.available


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

def build_registry():
    registry = ToolRegistry()

    github = FakeTool(
        "github",
        {Capability.CODE_SEARCH},
    )

    browser = FakeTool(
        "browser",
        {
            Capability.CODE_SEARCH,
            Capability.WEB_BROWSE,
        },
    )

    search = FakeTool(
        "web_search",
        {Capability.WEB_BROWSE},
    )

    registry.register(github)
    registry.register(browser)
    registry.register(search)

    return registry


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_register_fallback():
    registry = build_registry()
    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser", "web_search"],
    )

    assert manager.has_fallback("github")
    assert manager.all()["github"] == ["browser", "web_search"]


def test_get_next_tool_returns_first_valid():
    registry = build_registry()
    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser", "web_search"],
    )

    tool = manager.get_next_tool(
        failed_tool="github",
        attempted_tools=[],
        capability=Capability.CODE_SEARCH,
    )

    assert tool is not None
    assert tool.name == "browser"


def test_skips_attempted_tools():
    registry = build_registry()
    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser", "web_search"],
    )

    tool = manager.get_next_tool(
        failed_tool="github",
        attempted_tools=["browser"],
        capability=Capability.WEB_BROWSE,
    )

    assert tool is not None
    assert tool.name == "web_search"


def test_skips_unavailable_tool():
    registry = ToolRegistry()

    browser = FakeTool(
        "browser",
        {Capability.WEB_BROWSE},
        available=False,
    )

    search = FakeTool(
        "web_search",
        {Capability.WEB_BROWSE},
    )

    registry.register(browser)
    registry.register(search)

    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser", "web_search"],
    )

    tool = manager.get_next_tool(
        failed_tool="github",
        attempted_tools=[],
        capability=Capability.WEB_BROWSE,
    )

    assert tool is not None
    assert tool.name == "web_search"


def test_skips_tool_without_required_capability():
    registry = ToolRegistry()

    browser = FakeTool(
        "browser",
        {Capability.WEB_BROWSE},
    )

    search = FakeTool(
        "web_search",
        {Capability.WEB_BROWSE},
    )

    registry.register(browser)
    registry.register(search)

    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser", "web_search"],
    )

    tool = manager.get_next_tool(
        failed_tool="github",
        attempted_tools=[],
        capability=Capability.CODE_SEARCH,
    )

    assert tool is None


def test_skips_missing_tool():
    registry = ToolRegistry()

    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser"],
    )

    tool = manager.get_next_tool(
        failed_tool="github",
        attempted_tools=[],
        capability=Capability.WEB_BROWSE,
    )

    assert tool is None


def test_returns_none_when_no_fallback_registered():
    registry = build_registry()
    manager = FallbackManager(registry)

    tool = manager.get_next_tool(
        failed_tool="unknown_tool",
        attempted_tools=[],
        capability=Capability.WEB_BROWSE,
    )

    assert tool is None


def test_returns_none_when_all_candidates_attempted():
    registry = build_registry()
    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser", "web_search"],
    )

    tool = manager.get_next_tool(
        failed_tool="github",
        attempted_tools=["browser", "web_search"],
        capability=Capability.WEB_BROWSE,
    )

    assert tool is None


def test_clear_removes_all_fallbacks():
    registry = build_registry()
    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser"],
    )

    manager.clear()

    assert manager.all() == {}
    assert not manager.has_fallback("github")


def test_all_returns_copy():
    registry = build_registry()
    manager = FallbackManager(registry)

    manager.register(
        "github",
        ["browser"],
    )

    fallbacks = manager.all()

    fallbacks["github"] = ["modified"]

    assert manager.all()["github"] == ["browser"]