"""
Integration test for complete agent execution pipeline.

Covers:

- AgentFactory
- AgentManager
- BaseAgent lifecycle
- AgentContext
- ExecutionEngine
- ToolRegistry
- ToolExecutor
"""


import pytest

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_context import AgentContext

from app.agents.manager.agent_factory import AgentFactory
from app.agents.manager.agent_manager import AgentManager

from app.agents.tools.tool_registry import ToolRegistry
from app.agents.tools.tool_executor import ToolExecutor


# ---------------------------------------------------------
# Fake Agent
# ---------------------------------------------------------


class TestAgent(BaseAgent):

    async def execute(
        self,
        context: AgentContext,
    ):

        context.set_output(
            "agent_result",
            "agent completed",
        )

        return {
            "status": "success",
            "message": "agent completed",
        }


# ---------------------------------------------------------
# Fake Tool
# ---------------------------------------------------------


class MockTool:

    name = "calculator"


    async def execute(
        self,
        value: int,
    ):

        return value * 2



# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture
def agent_factory():

    factory = AgentFactory()

    factory.register(
        "test",
        TestAgent,
    )

    return factory



@pytest.fixture
def agent_manager(
    agent_factory,
):

    return AgentManager(
        factory=agent_factory
    )



@pytest.fixture
def context():

    return AgentContext(
        query="test query",
        task="test execution",
    )



@pytest.fixture
def tool_registry():

    registry = ToolRegistry()

    registry.register(
        MockTool()
    )

    return registry



# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_agent_creation_pipeline(
    agent_manager,
):

    """
    AgentFactory -> AgentManager
    """

    agent = agent_manager.create_agent(
        name="test_agent",
        agent_type="test",
        name="test-agent",
    )


    assert agent is not None

    assert isinstance(
        agent,
        BaseAgent,
    )


    assert agent_manager.has_agent(
        "test_agent"
    )


    assert agent_manager.count() == 1



@pytest.mark.asyncio
async def test_agent_execution_pipeline(
    agent_manager,
    context,
):

    """
    AgentManager -> BaseAgent.run()
    """

    agent = agent_manager.create_agent(
        name="executor",
        agent_type="test",
        name="executor",
    )


    result = await agent.run(
        context
    )


    assert result["status"] == "success"


    assert (
        context.get_output(
            "agent_result"
        )
        ==
        "agent completed"
    )



@pytest.mark.asyncio
async def test_agent_failure_handling(
    context,
):


    class FailingAgent(BaseAgent):

        async def execute(
            self,
            context,
        ):

            raise RuntimeError(
                "agent failed"
            )


    agent = FailingAgent(
        name="failure-agent"
    )


    with pytest.raises(
        RuntimeError
    ):

        await agent.run(
            context
        )


    assert (
        "agent failed"
        in context.errors
    )



@pytest.mark.asyncio
async def test_tool_execution_pipeline(
    tool_registry,
):

    """
    ToolRegistry -> ToolExecutor
    """


    executor = ToolExecutor(
        tool_registry
    )


    result = await executor.execute(
        "calculator",
        value=10,
    )


    assert result == 20



@pytest.mark.asyncio
async def test_complete_agent_tool_flow(
    agent_manager,
    context,
    tool_registry,
):

    """
    Complete simplified pipeline:

    Agent
      |
      v
    Context
      |
      v
    Tool execution
    """


    agent = agent_manager.create_agent(
        name="pipeline-agent",
        agent_type="test",
        name="pipeline-agent",
    )


    agent_result = await agent.run(
        context
    )


    executor = ToolExecutor(
        tool_registry
    )


    tool_result = await executor.execute(
        "calculator",
        value=5,
    )


    assert agent_result["status"] == "success"

    assert tool_result == 10


    assert (
        context.outputs["agent_result"]
        ==
        "agent completed"
    )