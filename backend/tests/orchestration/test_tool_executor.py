import pytest

from app.orchestration.tool_executor import ToolExecutor

from tests.orchestration.conftest import FakeTool



@pytest.mark.asyncio
async def test_execute_success():

    executor = ToolExecutor()


    tool = FakeTool()


    result = await executor.execute(
        tool
    )


    assert result.success is True

    assert result.tool_name=="fake_tool"

    assert result.data["message"]=="success"




@pytest.mark.asyncio
async def test_execute_failure():

    executor = ToolExecutor(
        max_retries=1
    )


    tool = FakeTool(
        should_fail=True
    )


    result = await executor.execute(
        tool
    )


    assert result.success is False

    assert result.error=="Tool failed"



@pytest.mark.asyncio
async def test_retry_behavior():

    executor = ToolExecutor(
        max_retries=3
    )


    tool = FakeTool(
        should_fail=True
    )


    result = await executor.execute(
        tool
    )


    assert result.success is False

    assert result.error is not None