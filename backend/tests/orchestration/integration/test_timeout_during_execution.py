import asyncio

import pytest

from app.orchestration.timeout_manager import TimeoutManager


@pytest.mark.asyncio
async def test_timeout_during_execution():
    """
    Verify that a long-running operation is terminated
    when it exceeds the configured timeout.
    """

    timeout_manager = TimeoutManager(default_timeout=0.1)

    async def slow_operation():
        await asyncio.sleep(1)
        return "completed"

    result = await timeout_manager.run(slow_operation)

    assert result.success is False
    assert result.timed_out is True
    assert result.output is None
    assert result.error is not None
    assert "timeout" in result.error.lower()