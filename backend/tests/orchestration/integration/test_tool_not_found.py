import pytest

from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine
from app.orchestration.capability import Capability


@pytest.mark.asyncio
async def test_tool_not_found(tool_registry):
    """
    If no tool exists for a capability,
    the orchestration service should fail immediately.
    """

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

    with pytest.raises(ValueError, match="No tool supports"):
        await service.execute(
            Capability.WEB_SEARCH,
            query="OpenAI",
        )