"""
Unit tests for:

- AgentRegistry
- CapabilityRegistry
- AgentSelector
"""

import pytest

from app.agents.base.base_agent import BaseAgent

from app.agents.registry.agent_registry import AgentRegistry
from app.agents.manager.agent_selector import AgentSelector
from app.agents.registry.capability_registry import CapabilityRegistry


# ---------------------------------------------------------
# Dummy Agents
# ---------------------------------------------------------


class MockAgent(BaseAgent):

    def __init__(self):
        super().__init__("mock")

    def execute(self, context=None):
        return "mock result"



class LowPriorityAgent(BaseAgent):

    priority = 1

    def __init__(self):
        super().__init__("low")

    def execute(self, context=None):
        return "low result"



class HighPriorityAgent(BaseAgent):

    priority = 10

    def __init__(self):
        super().__init__("high")

    def execute(self, context=None):
        return "high result"


# =========================================================
# AgentRegistry Tests
# =========================================================


class TestAgentRegistry:

    def test_initial_registry_empty(self):

        registry = AgentRegistry()

        assert len(registry) == 0
        assert registry.list_agents() == []


    def test_register_agent(self):

        registry = AgentRegistry()

        registry.register(
            "mock",
            MockAgent,
        )

        assert len(registry) == 1
        assert registry.exists("mock")


    def test_duplicate_registration(self):

        registry = AgentRegistry()

        registry.register(
            "mock",
            MockAgent,
        )

        with pytest.raises(ValueError):

            registry.register(
                "mock",
                MockAgent,
            )


    def test_get_agent(self):

        registry = AgentRegistry()

        registry.register(
            "mock",
            MockAgent,
        )

        result = registry.get("mock")

        assert result == MockAgent


    def test_get_missing_agent(self):

        registry = AgentRegistry()

        assert registry.get("missing") is None


    def test_unregister_agent(self):

        registry = AgentRegistry()

        registry.register(
            "mock",
            MockAgent,
        )

        registry.unregister("mock")

        assert not registry.exists("mock")


    def test_unregister_missing_agent_safe(self):

        registry = AgentRegistry()

        registry.unregister("unknown")

        assert len(registry) == 0


    def test_list_agents_sorted(self):

        registry = AgentRegistry()

        registry.register(
            "z_agent",
            MockAgent,
        )

        registry.register(
            "a_agent",
            MockAgent,
        )

        assert registry.list_agents() == [
            "a_agent",
            "z_agent",
        ]


    def test_clear_registry(self):

        registry = AgentRegistry()

        registry.register(
            "mock",
            MockAgent,
        )

        registry.clear()

        assert len(registry) == 0


    def test_contains(self):

        registry = AgentRegistry()

        registry.register(
            "mock",
            MockAgent,
        )

        assert "mock" in registry


    def test_repr(self):

        registry = AgentRegistry()

        assert repr(registry) == (
            "AgentRegistry(0 agents)"
        )


# =========================================================
# CapabilityRegistry Tests
# =========================================================


class TestCapabilityRegistry:


    def test_register_capability(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "BrowserAgent",
        )

        assert registry.has_capability("search")


    def test_multiple_agents_same_capability(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "BrowserAgent",
        )

        registry.register(
            "search",
            "ResearchAgent",
        )

        assert registry.get_agents("search") == [
            "BrowserAgent",
            "ResearchAgent",
        ]


    def test_duplicate_registration_is_ignored(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "BrowserAgent",
        )

        registry.register(
            "search",
            "BrowserAgent",
        )

        assert registry.get_agents("search") == [
            "BrowserAgent"
        ]


    def test_unregister_capability_agent(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "BrowserAgent",
        )

        registry.unregister(
            "search",
            "BrowserAgent",
        )

        assert not registry.has_capability("search")


    def test_get_missing_capability(self):

        registry = CapabilityRegistry()

        assert registry.get_agents("missing") == []


    def test_list_capabilities(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "Browser",
        )

        registry.register(
            "code",
            "Coder",
        )

        assert registry.list_capabilities() == [
            "code",
            "search",
        ]


    def test_capabilities_for_agent(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "Browser",
        )

        registry.register(
            "crawl",
            "Browser",
        )

        assert registry.capabilities_for_agent("Browser") == [
            "crawl",
            "search",
        ]


    def test_remove_agent(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "Browser",
        )

        registry.register(
            "crawl",
            "Browser",
        )

        registry.remove_agent("Browser")

        assert len(registry) == 0


    def test_export(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "Browser",
        )

        assert registry.export() == {
            "search": [
                "Browser"
            ]
        }


    def test_clear(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "Browser",
        )

        registry.clear()

        assert len(registry) == 0


    def test_contains(self):

        registry = CapabilityRegistry()

        registry.register(
            "search",
            "Browser",
        )

        assert "search" in registry


# =========================================================
# AgentSelector Tests
# =========================================================


class TestAgentSelector:


    def setup_method(self):

        self.cap_registry = CapabilityRegistry()

        self.selector = AgentSelector(
            self.cap_registry
        )


    def test_select_no_agent(self):

        result = self.selector.select(
            "missing"
        )

        assert result is None


    def test_rank_agents(self):

        agents = [
            LowPriorityAgent(),
            HighPriorityAgent(),
        ]

        ranked = self.selector.rank_agents(
            agents
        )

        assert ranked[0].priority == 10


    def test_select_highest_priority(self):

        high = HighPriorityAgent()
        low = LowPriorityAgent()

        self.cap_registry.find_agents = lambda cap: [
            low,
            high,
        ]

        result = self.selector.select(
            "code"
        )

        assert result == high


    def test_select_multiple(self):

        agents = [
            HighPriorityAgent(),
            LowPriorityAgent(),
        ]

        self.cap_registry.find_agents = lambda cap: agents

        result = self.selector.select_multiple(
            "code",
            limit=1,
        )

        assert len(result) == 1
        assert result[0].priority == 10


    def test_supports(self):

        self.cap_registry.find_agents = lambda cap: [
            HighPriorityAgent()
        ]

        assert self.selector.supports("code")


    def test_available_agents(self):

        self.cap_registry.list_agents = lambda: [
            "AgentA"
        ]

        assert self.selector.available_agents() == [
            "AgentA"
        ]


    def test_capabilities(self):

        self.cap_registry.capabilities = lambda: [
            "search"
        ]

        assert self.selector.capabilities() == [
            "search"
        ]


    def test_summary(self):

        self.cap_registry.list_agents = lambda: [
            "AgentA",
            "AgentB",
        ]

        self.cap_registry.capabilities = lambda: [
            "search"
        ]

        assert self.selector.summary() == {
            "agents": 2,
            "capabilities": 1,
        }