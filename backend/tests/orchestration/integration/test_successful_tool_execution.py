import pytest

from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_registry import ToolRegistry
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine
from app.orchestration.capability import Capability

from tests.helpers.fake_tool  import FakeTool


@pytest.mark.asyncio
async def test_successful_tool_execution():
    """
    End-to-end integration test.

    Registry
        ↓
    Health Check
        ↓
    Policy Check
        ↓
    Tool Selection
        ↓
    Tool Execution
    """

    registry = ToolRegistry()

    tool =  FakeTool(
        name="search_tool",
        priority=10,
        enabled=True,
        healthy=True,
        capabilities=[Capability.WEB_SEARCH],
    )

    registry.register(tool)

    selector = ToolSelector(registry)
    executor = ToolExecutor()

    health_monitor = HealthMonitor()
    policy_engine = PolicyEngine()

    service = OrchestrationService(
        registry=registry,
        selector=selector,
        executor=executor,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )

    result = await service.execute(
        Capability.WEB_SEARCH,
        query="OpenAI",
    )

    assert result == {
        "message": "success"
    }