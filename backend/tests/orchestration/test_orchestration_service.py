import pytest

from unittest.mock import Mock

from app.orchestration.orchestration_service import (
    OrchestrationService
)

from app.orchestration.tool_registry import (
    ToolRegistry
)

from app.orchestration.tool_selector import (
    ToolSelector
)

from app.orchestration.tool_executor import (
    ToolExecutor
)

from app.orchestration.capability import (
    Capability
)

from tests.orchestration.conftest import (
    FakeTool
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def search_tool():

    return FakeTool(
        name="search_tool",
        priority=10,
        capabilities=[
            Capability.WEB_SEARCH
        ]
    )



@pytest.fixture
def registry(
    search_tool
):

    registry = ToolRegistry()

    registry.register(
        search_tool
    )

    return registry



@pytest.fixture
def health_monitor():

    monitor = Mock()

    monitor.is_available.return_value = True

    return monitor



@pytest.fixture
def policy_engine():

    policy = Mock()

    policy.filter.side_effect = (
        lambda tools, **kwargs: tools
    )

    return policy



@pytest.fixture
def service(
    registry,
    health_monitor,
    policy_engine
):

    selector = ToolSelector(
        registry
    )


    executor = ToolExecutor()


    return OrchestrationService(
        registry=registry,
        selector=selector,
        executor=executor,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )



# ============================================================
# Success Flow
# ============================================================


@pytest.mark.asyncio
async def test_execute_success(
    service
):

    result = await service.execute(
        Capability.WEB_SEARCH,
        query="latest AI news"
    )


    assert result.success is True

    assert result.tool_name=="search_tool"



# ============================================================
# No Tool Available
# ============================================================


@pytest.mark.asyncio
async def test_execute_without_tool():

    registry = ToolRegistry()


    service = OrchestrationService(
        registry=registry,
        selector=ToolSelector(registry),
        executor=ToolExecutor(),
        health_monitor=Mock(),
        policy_engine=Mock(),
    )


    with pytest.raises(
        ValueError
    ):

        await service.execute(
            Capability.WEB_SEARCH
        )



# ============================================================
# Unhealthy Tool
# ============================================================


@pytest.mark.asyncio
async def test_unhealthy_tool(
    registry,
    health_monitor,
    policy_engine
):

    health_monitor.is_available.return_value=False


    service = OrchestrationService(
        registry=registry,
        selector=ToolSelector(registry),
        executor=ToolExecutor(),
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )


    with pytest.raises(
        RuntimeError
    ):

        await service.execute(
            Capability.WEB_SEARCH
        )



# ============================================================
# Policy Rejection
# ============================================================


@pytest.mark.asyncio
async def test_policy_blocks_tool(
    registry,
    health_monitor
):

    policy_engine = Mock()

    policy_engine.filter.return_value=[]


    service = OrchestrationService(
        registry=registry,
        selector=ToolSelector(registry),
        executor=ToolExecutor(),
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )


    with pytest.raises(
        PermissionError
    ):

        await service.execute(
            Capability.WEB_SEARCH
        )



# ============================================================
# Executor Failure
# ============================================================


@pytest.mark.asyncio
async def test_executor_failure(
    registry,
    health_monitor,
    policy_engine
):

    executor = Mock()


    executor.execute.side_effect = Exception(
        "execution failed"
    )


    service = OrchestrationService(
        registry=registry,
        selector=ToolSelector(registry),
        executor=executor,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )


    with pytest.raises(
        Exception
    ):

        await service.execute(
            Capability.WEB_SEARCH
        )