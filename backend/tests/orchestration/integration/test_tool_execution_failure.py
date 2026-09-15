from __future__ import annotations

import pytest

from app.orchestration.capability import Capability
from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.tool_registry import ToolRegistry
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine
from app.orchestration.retry_manager import RetryManager
from tests.helpers.fake_tool import FakeTool


@pytest.mark.asyncio
async def test_tool_execution_failure():
    """
    Verify that a failing tool returns an unsuccessful
    ToolExecutionResult instead of crashing the orchestration layer.
    """

    registry = ToolRegistry()

    failing_tool = FakeTool(
        name="failing_tool",
        should_fail=True,
    )
    retry_manager = RetryManager(max_retries=0)
    registry.register(failing_tool)

    selector = ToolSelector(registry)
    executor = ToolExecutor(max_retries=0)
    health_monitor = HealthMonitor()
    policy_engine = PolicyEngine()

    service = OrchestrationService(
        registry=registry,
        retry_manager=retry_manager,
        selector=selector,
        executor=executor,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )

    result = await service.execute(
        Capability.WEB_SEARCH,
        query="OpenAI",
    )

    assert result.success is False
    assert result.tool_name == "failing_tool"
    assert result.data is None
    assert result.error == "Tool failed"
    assert result.latency >= 0