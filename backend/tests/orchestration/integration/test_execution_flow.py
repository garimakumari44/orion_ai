import pytest

from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine
from app.orchestration.capability import Capability


@pytest.mark.asyncio
async def test_successful_tool_execution(
    tool_registry,
    fake_tool,
):
    """
    End-to-end orchestration flow.

    Registry
        ↓
    Health Check
        ↓
    Policy
        ↓
    Selection
        ↓
    Execution
        ↓
    Success
    """

    # Register tool
    tool_registry.register(fake_tool)

    selector = ToolSelector(tool_registry)
    executor = ToolExecutor()
    health_monitor = HealthMonitor()
    policy_engine = PolicyEngine()

    service = OrchestrationService(
        registry=tool_registry,
        selector=selector,
        executor=executor,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )

    result = await service.execute(
        Capability.WEB_SEARCH,
        query="OpenAI",
    )

    assert result.success is True
    assert result.tool_name == fake_tool.name
    assert result.data == {
        "message": "success"
    }
    assert result.error is None
    assert result.latency >= 0