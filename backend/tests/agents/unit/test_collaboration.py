"""
Unit tests for Collaboration package

Covers:
- MessageBus
- SharedWorkspace
- ResponseSynthesizer
- ConflictResolver
- CollaborationManager
"""

import asyncio
import pytest

from app.agents.collaboration.messaging import (
    MessageBus,
    AgentMessage,
    MessageType,
)

from app.agents.collaboration.workspace import (
    SharedWorkspace,
)

from app.agents.collaboration.result_synthesizer import (
    ResponseSynthesizer,
    AgentResponse,
)

from app.agents.collaboration.collaboration_manager import (
    CollaborationManager,
    CollaborationResult,
)


# ============================================================
# MessageBus Tests
# ============================================================


@pytest.mark.asyncio
async def test_message_bus_register_and_send():

    bus = MessageBus()

    bus.register_agent("agent_a")
    bus.register_agent("agent_b")


    message = AgentMessage(
        sender="agent_a",
        receiver="agent_b",
        message_type=MessageType.REQUEST,
        payload="hello",
    )


    await bus.send(message)


    received = await bus.receive(
        "agent_b"
    )


    assert received.payload == "hello"
    assert received.sender == "agent_a"



@pytest.mark.asyncio
async def test_message_bus_broadcast():

    bus = MessageBus()

    bus.register_agent("agent_a")
    bus.register_agent("agent_b")
    bus.register_agent("agent_c")


    await bus.broadcast(
        sender="agent_a",
        payload="broadcast message",
    )


    msg1 = await bus.receive("agent_b")
    msg2 = await bus.receive("agent_c")


    assert msg1.payload == "broadcast message"
    assert msg2.payload == "broadcast message"



def test_message_history():

    bus = MessageBus()

    bus.register_agent("a")
    bus.register_agent("b")


    msg = AgentMessage(
        sender="a",
        receiver="b",
        message_type=MessageType.EVENT,
        payload="event",
    )


    asyncio.run(
        bus.send(msg)
    )


    history = bus.history()


    assert len(history) == 1
    assert history[0].payload == "event"



# ============================================================
# Workspace Tests
# ============================================================


@pytest.mark.asyncio
async def test_workspace_store_and_get_result():

    workspace = SharedWorkspace()


    await workspace.store_result(
        "agent1",
        {"answer": 42},
    )


    result = await workspace.get_result(
        "agent1"
    )


    assert result == {
        "answer":42
    }



@pytest.mark.asyncio
async def test_workspace_artifacts():

    workspace = SharedWorkspace()


    await workspace.add_artifact(
        "agent1",
        "artifact-data",
    )


    artifacts = await workspace.get_artifacts(
        "agent1"
    )


    assert artifacts == [
        "artifact-data"
    ]



@pytest.mark.asyncio
async def test_workspace_shared_memory():

    workspace = SharedWorkspace()


    await workspace.put(
        "key",
        "value",
    )


    result = await workspace.get(
        "key"
    )


    assert result == "value"


    assert await workspace.contains(
        "key"
    )



@pytest.mark.asyncio
async def test_workspace_summary():

    workspace = SharedWorkspace()


    await workspace.store_result(
        "agent1",
        "result",
    )

    summary = await workspace.summary()


    assert summary["agents"] == 1



# ============================================================
# Synthesizer Tests
# ============================================================


def test_response_synthesizer_empty():

    synthesizer = ResponseSynthesizer()


    result = synthesizer.synthesize(
        []
    )


    assert result.content == ""
    assert result.confidence == 0



def test_response_synthesizer_merge():

    synthesizer = ResponseSynthesizer()


    responses = [

        AgentResponse(
            agent="agent1",
            content="Python is fast",
            confidence=0.8,
            evidence=["doc1"],
        ),

        AgentResponse(
            agent="agent2",
            content="Python is popular",
            confidence=0.9,
            evidence=["doc2"],
        ),

    ]


    result = synthesizer.synthesize(
        responses
    )


    assert (
        "Python is popular"
        in result.content
    )

    assert result.confidence == 0.85

    assert len(
        result.evidence
    ) == 2



# ============================================================
# Conflict Resolver Mock
# ============================================================


class MockConflictResolver:

    async def resolve(self, results):

        return results



# ============================================================
# Agent Mock
# ============================================================


class MockAgent:


    def __init__(self, name):

        self.name = name



    async def run(
        self,
        task,
        context,
    ):

        return {
            "agent":self.name,
            "output":"done",
        }



# ============================================================
# Synthesizer Mock
# ============================================================


class MockSynthesizer:


    async def synthesize(
        self,
        task,
        results,
        context,
    ):

        return {
            "task":task,
            "results":results,
        }



# ============================================================
# Collaboration Manager Tests
# ============================================================


@pytest.mark.asyncio
async def test_collaboration_manager_success():


    workspace = SharedWorkspace()

    bus = MessageBus()


    manager = CollaborationManager(
        workspace=workspace,
        message_bus=bus,
        synthesizer=MockSynthesizer(),
        conflict_resolver=MockConflictResolver(),
    )


    agents = [
        MockAgent("agent1"),
        MockAgent("agent2"),
    ]


    result = await manager.collaborate(
        task="analyze data",
        agents=agents,
        context=None,
    )


    assert isinstance(
        result,
        CollaborationResult
    )


    assert result.success is True


    assert len(
        result.agents
    ) == 2



@pytest.mark.asyncio
async def test_collaboration_manager_failure():


    workspace = SharedWorkspace()

    bus = MessageBus()



    class BrokenAgent:

        name="broken"


        async def run(
            self,
            task,
            context,
        ):
            raise Exception(
                "agent failed"
            )



    manager = CollaborationManager(
        workspace,
        bus,
        MockSynthesizer(),
        MockConflictResolver(),
    )


    result = await manager.collaborate(
        task="test",
        agents=[
            BrokenAgent()
        ],
        context=None,
    )


    assert result.success is True