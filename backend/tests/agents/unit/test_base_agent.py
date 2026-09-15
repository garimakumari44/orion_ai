"""
Tests for BaseAgent.
"""

import pytest

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_context import AgentContext


class SuccessAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="success",
            description="Successful test agent",
            capabilities={"testing"},
        )

    async def execute(self, context: AgentContext):
        context.set_output("result", 123)
        context.set_state("status", "done")
        context.remember("cached", True)

        return {"success": True}


class FailureAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="failure",
            description="Failure test agent",
            capabilities={"testing"},
        )

    async def execute(self, context: AgentContext):
        raise RuntimeError("agent failed")


# ---------------------------------------------------------------------
# BaseAgent.run()
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_success():

    context = AgentContext(query="hello")

    agent = SuccessAgent()

    result = await agent.run(context)

    assert result == {"success": True}

    assert context.get_output("result") == 123

    assert context.get_state("status") == "done"

    assert context.recall("cached") is True

    assert context.errors == []


@pytest.mark.asyncio
async def test_run_failure():

    context = AgentContext(query="hello")

    agent = FailureAgent()

    with pytest.raises(RuntimeError):
        await agent.run(context)

    assert len(context.errors) == 1

    assert context.errors[0] == "agent failed"


# ---------------------------------------------------------------------
# supports()
# ---------------------------------------------------------------------


def test_supports():

    agent = SuccessAgent()

    assert agent.supports("testing") is True

    assert agent.supports("research") is False


# ---------------------------------------------------------------------
# AgentContext helpers
# ---------------------------------------------------------------------


def test_agent_context():

    context = AgentContext(query="AI")

    context.set_output("summary", "done")
    context.set_state("phase", 2)
    context.remember("company", "OpenAI")
    context.add_error("network")

    assert context.get_output("summary") == "done"

    assert context.get_state("phase") == 2

    assert context.recall("company") == "OpenAI"

    assert context.errors == ["network"]