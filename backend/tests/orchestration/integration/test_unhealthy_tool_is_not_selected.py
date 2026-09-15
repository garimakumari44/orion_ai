import pytest

from app.orchestration.capability import Capability
from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.health_monitor import HealthMonitor
from tests.helpers.fake_tool  import FakeTool
from app.orchestration.policies import PolicyEngine, PolicyResult
from app.orchestration.retry_manager import RetryManager


class FakePolicyEngine:
    def filter(self, tools, capability):
        return tools


@pytest.mark.asyncio
async def test_unhealthy_tool_is_not_selected(tool_registry):
    """
    Highest-priority unhealthy tool should be skipped and
    the healthy tool should be executed instead.
    """

    unhealthy_tool = FakeTool(
        name="primary_tool",
        priority=10,
        capabilities=[Capability.WEB_SEARCH],
    )

    healthy_tool = FakeTool(
        name="backup_tool",
        priority=5,
        capabilities=[Capability.WEB_SEARCH],
    )

    tool_registry.register(unhealthy_tool)
    tool_registry.register(healthy_tool)

    health_monitor = HealthMonitor()

    # Register both tools
    health_monitor.register_tool("primary_tool")
    health_monitor.register_tool("backup_tool")

    # Make primary tool unhealthy
    health_monitor.record_failure("primary_tool", "error")
    health_monitor.record_failure("primary_tool", "error")
    health_monitor.record_failure("primary_tool", "error")

    service = OrchestrationService(
         registry=tool_registry,
         selector=ToolSelector(tool_registry),
         executor=ToolExecutor(),
         health_monitor=HealthMonitor(),
         policy_engine=PolicyEngine(),
         retry_manager=RetryManager(
        max_retries=1,
        initial_delay=0,
    ),
)
    result = await service.execute(Capability.WEB_SEARCH)

    assert result == {"message": "success"}

    assert health_monitor.is_healthy("primary_tool") is False
    assert health_monitor.is_healthy("backup_tool") is True