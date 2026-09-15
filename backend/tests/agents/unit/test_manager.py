"""
Unit tests for AgentFactory, AgentManager, and AgentSelector.
"""

from unittest.mock import Mock

import pytest

from app.agents.base.base_agent import BaseAgent
from app.agents.manager.agent_factory import AgentFactory
from app.agents.manager.agent_manager import AgentManager
from app.agents.manager.agent_selector import AgentSelector


# ==========================================================
# Dummy Agent
# ==========================================================


class DummyAgent(BaseAgent):
    def __init__(self, name="dummy"):
        super().__init__(name=name)

    async def execute(self, context):
        return "executed"

    async def receive(self, message):
        return f"received: {message}"


# ==========================================================
# AgentFactory Tests
# ==========================================================


class TestAgentFactory:
    def test_register_agent(self):
        factory = AgentFactory()

        factory.register("dummy", DummyAgent)

        assert factory.is_registered("dummy")

    def test_register_duplicate_agent_raises(self):
        factory = AgentFactory()

        factory.register("dummy", DummyAgent)

        with pytest.raises(ValueError):
            factory.register("dummy", DummyAgent)

    def test_create_agent(self):
        factory = AgentFactory()

        factory.register("dummy", DummyAgent)

        agent = factory.create("dummy")

        assert isinstance(agent, DummyAgent)

    def test_create_unknown_agent_raises(self):
        factory = AgentFactory()

        with pytest.raises(ValueError):
            factory.create("missing")

    def test_available_agents(self):
        factory = AgentFactory()

        factory.register("dummy", DummyAgent)

        assert factory.available_agents() == ["dummy"]

    def test_unregister(self):
        factory = AgentFactory()

        factory.register("dummy", DummyAgent)

        factory.unregister("dummy")

        assert not factory.is_registered("dummy")

    def test_clear(self):
        factory = AgentFactory()

        factory.register("dummy", DummyAgent)

        factory.clear()

        assert factory.available_agents() == []


# ==========================================================
# AgentManager Tests
# ==========================================================


class TestAgentManager:
    def setup_method(self):
        self.factory = AgentFactory()
        self.factory.register("dummy", DummyAgent)
        self.manager = AgentManager(self.factory)

    def test_create_agent(self):
        agent = self.manager.create_agent("agent1", "dummy")

        assert isinstance(agent, DummyAgent)

    def test_duplicate_agent_name_raises(self):
        self.manager.create_agent("agent1", "dummy")

        with pytest.raises(ValueError):
            self.manager.create_agent("agent1", "dummy")

    def test_get_agent(self):
        created = self.manager.create_agent("agent1", "dummy")

        retrieved = self.manager.get_agent("agent1")

        assert retrieved is created

    def test_get_unknown_agent(self):
        with pytest.raises(KeyError):
            self.manager.get_agent("missing")

    def test_has_agent(self):
        self.manager.create_agent("agent1", "dummy")

        assert self.manager.has_agent("agent1")
        assert not self.manager.has_agent("missing")

    def test_list_agents(self):
        self.manager.create_agent("b", "dummy")
        self.manager.create_agent("a", "dummy")

        assert self.manager.list_agents() == ["a", "b"]

    def test_remove_agent(self):
        self.manager.create_agent("agent1", "dummy")

        self.manager.remove_agent("agent1")

        assert not self.manager.has_agent("agent1")

    def test_clear(self):
        self.manager.create_agent("a", "dummy")
        self.manager.create_agent("b", "dummy")

        self.manager.clear()

        assert self.manager.count() == 0

    @pytest.mark.asyncio
    async def test_broadcast(self):
        self.manager.create_agent("a", "dummy")
        self.manager.create_agent("b", "dummy")

        result = await self.manager.broadcast("hello")

        assert result == {
            "a": "received: hello",
            "b": "received: hello",
        }

    def test_count(self):
        assert self.manager.count() == 0

        self.manager.create_agent("a", "dummy")

        assert self.manager.count() == 1


# ==========================================================
# AgentSelector Tests
# ==========================================================


class TestAgentSelector:
    def setup_method(self):
        self.registry = Mock()
        self.selector = AgentSelector(self.registry)

    def test_select_returns_first_agent(self):
        agent1 = Mock(spec=BaseAgent)
        agent1.name = "agent1"

        agent2 = Mock(spec=BaseAgent)
        agent2.name = "agent2"

        self.registry.find_agents.return_value = [agent1, agent2]

        result = self.selector.select("code")

        assert result is agent1

    def test_select_returns_none_when_missing(self):
        self.registry.find_agents.return_value = []

        assert self.selector.select("unknown") is None

    def test_select_many(self):
        agent1 = Mock(spec=BaseAgent)
        agent1.name = "research"

        agent2 = Mock(spec=BaseAgent)
        agent2.name = "writer"

        self.selector.select = Mock(side_effect=[agent1, agent2])

        result = self.selector.select_many(
            ["research", "writing"]
        )

        assert result == [agent1, agent2]

    def test_select_many_removes_duplicates(self):
        agent = Mock(spec=BaseAgent)
        agent.name = "shared"

        self.selector.select = Mock(side_effect=[agent, agent])

        result = self.selector.select_many(["a", "b"])

        assert result == [agent]

    def test_select_many_skips_none(self):
        agent = Mock(spec=BaseAgent)
        agent.name = "writer"

        self.selector.select = Mock(side_effect=[None, agent])

        result = self.selector.select_many(["x", "y"])

        assert result == [agent]

    def test_has_capability(self):
        self.registry.has_capability.return_value = True

        assert self.selector.has_capability("code")

        self.registry.has_capability.assert_called_once_with("code")

    def test_available_capabilities(self):
        self.registry.capabilities.return_value = [
            "code",
            "research",
            "writing",
        ]

        assert self.selector.available_capabilities() == [
            "code",
            "research",
            "writing",
        ]