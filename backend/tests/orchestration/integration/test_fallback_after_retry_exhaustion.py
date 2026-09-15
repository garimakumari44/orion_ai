import pytest

from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine
from app.orchestration.retry_manager import RetryManager
from app.orchestration.fallback_manager import FallbackManager
from app.orchestration.capability import Capability
from tests.helpers.fake_tool  import FakeTool


@pytest.mark.asyncio
async def test_fallback_after_retry_exhaustion(tool_registry):

    failing_tool = FakeTool(
        name="primary",
        should_fail=True,
    )

    fallback_tool = FakeTool(
        name="fallback",
        should_fail=False,
    )

    tool_registry.register(failing_tool)
    tool_registry.register(fallback_tool)

    fallback_manager = FallbackManager(tool_registry)

    fallback_manager.register(
        "primary",
        ["fallback"],
    )

    service = OrchestrationService(
        registry=tool_registry,
        selector=ToolSelector(tool_registry),
        executor=ToolExecutor(max_retries=0),
        health_monitor=HealthMonitor(),
        policy_engine=PolicyEngine(),
        retry_manager=RetryManager(max_retries=1, initial_delay=0),
        fallback_manager=fallback_manager,
    )

    result = await service.execute(
        Capability.WEB_SEARCH
    )

    assert result.success is True
    assert result.tool_name == "fallback"