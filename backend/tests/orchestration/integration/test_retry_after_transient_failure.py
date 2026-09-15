import pytest

from app.orchestration.tool_executor import ToolExecutor
from tests.helpers.fake_tool  import FakeTool


@pytest.mark.asyncio
async def test_retry_after_transient_failure():
    """
    Tool fails once, succeeds on retry.
    """

    tool = FakeTool(fail_times=1)

    executor = ToolExecutor(
        max_retries=2,
    )

    result = await executor.execute(tool)

    assert result.success is True
    assert result.data == {"message": "success"}
    assert result.error is None

    # One failure + one successful retry
    assert tool.execution_count == 2