import pytest

from app.orchestration.orchestration_service import OrchestrationService
from app.orchestration.tool_registry import ToolRegistry
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.tool_executor import ToolExecutor
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.capability import Capability

from tests.helpers.fake_tool  import FakeTool


class BlockingPolicyEngine:
    """
    Reject every tool.
    """

    def filter(self, tools, capability):
        return []


@pytest.mark.asyncio
async def test_policy_blocks_execution():
    """
    Integration test:

    Registry
        ↓
    Health Check
        ↓
    Policy Engine blocks every tool
        ↓
    PermissionError
    """

    registry = ToolRegistry()

    registry.register(
        FakeTool(
            name="search_tool",
            capabilities=[Capability.WEB_SEARCH],
            healthy=True,
            enabled=True,
        )
    )

    selector = ToolSelector(registry)
    executor = ToolExecutor()
    health_monitor = HealthMonitor()
    policy_engine = BlockingPolicyEngine()

    service = OrchestrationService(
        registry=registry,
        selector=selector,
        executor=executor,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )

    with pytest.raises(
        PermissionError,
        match="All tools rejected by policy",
    ):
        await service.execute(
            Capability.WEB_SEARCH,
            query="OpenAI",
        )