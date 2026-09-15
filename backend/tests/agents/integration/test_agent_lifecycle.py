"""
Integration tests for complete agent lifecycle.

Covers:

- AgentConfig
- AgentContext
- BaseAgent execution
- AgentFactory
- AgentManager
- AgentRegistry
- CapabilityRegistry
- AgentSelector
"""

import pytest

from app.agents.base.agent_config import AgentConfig
from app.agents.base.agent_context import AgentContext
from app.agents.base.base_agent import BaseAgent

from app.agents.manager.agent_factory import AgentFactory
from app.agents.manager.agent_manager import AgentManager

from app.agents.registry.agent_registry import AgentRegistry
from app.agents.registry.capability_registry import CapabilityRegistry
from app.agents.manager.agent_selector import AgentSelector


# ============================================================
# Mock Agent
# ============================================================


class ResearchAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="research_agent",
            description="Research agent",
            capabilities={
                "research",
                "analysis",
            },
        )


    async def execute(
        self,
        context: AgentContext,
    ):

        context.set_output(
            "result",
            "research completed",
        )

        return {
            "status": "success",
            "agent": self.name,
        }



# ============================================================
# Agent Config Lifecycle
# ============================================================


def test_agent_config_lifecycle():

    config = AgentConfig(
        name="research_agent",
        description="Research worker",
        capabilities=[
            "research"
        ],
    )


    assert config.name == "research_agent"


    assert config.supports(
        "research"
    )


    config.add_capability(
        "analysis"
    )


    assert config.supports(
        "analysis"
    )


    config.remove_capability(
        "research"
    )


    assert not config.supports(
        "research"
    )


    config.update_metadata(
        "version",
        1,
    )


    assert config.get_metadata(
        "version"
    ) == 1




# ============================================================
# Agent Context Lifecycle
# ============================================================


def test_agent_context_lifecycle():

    context = AgentContext(
        query="Analyze AI market"
    )


    context.set_state(
        "started",
        True,
    )


    context.remember(
        "user_preference",
        "technical",
    )


    context.set_output(
        "answer",
        "done",
    )


    assert context.get_state(
        "started"
    )


    assert context.recall(
        "user_preference"
    ) == "technical"


    assert context.get_output(
        "answer"
    ) == "done"




# ============================================================
# Base Agent Execution
# ============================================================


@pytest.mark.asyncio
async def test_agent_execution_lifecycle():

    agent = ResearchAgent()


    context = AgentContext(
        query="Research AI"
    )


    result = await agent.run(
        context
    )


    assert result["status"] == "success"


    assert context.get_output(
        "result"
    ) == "research completed"




# ============================================================
# Factory + Manager Lifecycle
# ============================================================


def test_factory_manager_lifecycle():

    factory = AgentFactory()


    factory.register(
        "research",
        ResearchAgent,
    )


    manager = AgentManager(
        factory
    )


    agent = manager.create_agent(
        name="primary_research",
        agent_type="research",
    )


    assert isinstance(
        agent,
        ResearchAgent,
    )


    assert manager.has_agent(
        "primary_research"
    )


    assert manager.count() == 1


    retrieved = manager.get_agent(
        "primary_research"
    )


    assert retrieved.name == "research_agent"


    manager.remove_agent(
        "primary_research"
    )


    assert manager.count() == 0




# ============================================================
# Agent Registry Lifecycle
# ============================================================


def test_registry_lifecycle():

    registry = AgentRegistry()


    registry.register(
        "research",
        ResearchAgent,
    )


    assert registry.exists(
        "research"
    )


    assert registry.get(
        "research"
    ) == ResearchAgent


    assert "research" in registry


    registry.unregister(
        "research"
    )


    assert not registry.exists(
        "research"
    )




# ============================================================
# Capability Registry Lifecycle
# ============================================================


def test_capability_registry_lifecycle():

    registry = CapabilityRegistry()


    registry.register(
        "research",
        "research_agent",
    )


    registry.register(
        "analysis",
        "research_agent",
    )


    assert registry.has_capability(
        "research"
    )


    assert registry.get_agents(
        "research"
    ) == [
        "research_agent"
    ]


    assert registry.capabilities_for_agent(
        "research_agent"
    ) == [
        "analysis",
        "research",
    ]




# ============================================================
# Agent Selector Lifecycle
# ============================================================


def test_agent_selector_lifecycle():

    registry = CapabilityRegistry()


    research_agent = ResearchAgent()


    registry.register(
        "research",
        research_agent,
    )


    selector = AgentSelector(
        registry
    )


    selected = selector.select(
        "research"
    )


    assert selected == research_agent


    assert selected.name == "research_agent"


    assert "research" in selector.available_capabilities()




# ============================================================
# Complete Agent Lifecycle
# ============================================================


@pytest.mark.asyncio
async def test_complete_agent_lifecycle():

    #
    # 1. Register agent class
    #

    agent_registry = AgentRegistry()


    agent_registry.register(
        "research",
        ResearchAgent,
    )


    assert agent_registry.exists(
        "research"
    )



    #
    # 2. Register capability
    #

    capability_registry = CapabilityRegistry()


    research_agent = ResearchAgent()


    capability_registry.register(
        "research",
        research_agent,
    )



    #
    # 3. Create factory
    #

    factory = AgentFactory()


    factory.register(
        "research",
        ResearchAgent,
    )



    #
    # 4. Create runtime manager
    #

    manager = AgentManager(
        factory
    )


    agent = manager.create_agent(
        name="research_runtime",
        agent_type="research",
    )


    assert manager.has_agent(
        "research_runtime"
    )



    #
    # 5. Select agent
    #

    selector = AgentSelector(
        capability_registry
    )


    selected = selector.select(
        "research"
    )


    assert selected == research_agent



    #
    # 6. Execute agent
    #

    context = AgentContext(
        query="Find AI trends"
    )


    result = await agent.run(
        context
    )


    assert result["status"] == "success"


    assert context.get_output(
        "result"
    ) == "research completed"



    #
    # 7. Cleanup
    #

    manager.clear()


    assert manager.count() == 0