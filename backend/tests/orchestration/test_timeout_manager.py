import asyncio

import pytest

from app.orchestration.timeout_manager import TimeoutManager


# ==========================================================
# Helper Operations
# ==========================================================

async def fast_operation():
    return "success"


async def slow_operation():
    await asyncio.sleep(0.2)
    return "finished"


async def failing_operation():
    raise RuntimeError("operation failed")


# ==========================================================
# Success
# ==========================================================

@pytest.mark.asyncio
async def test_timeout_success():
    manager = TimeoutManager(default_timeout=1)

    result = await manager.run(fast_operation)

    assert result.success is True
    assert result.output == "success"
    assert result.error is None
    assert result.timed_out is False
    assert result.execution_time >= 0


# ==========================================================
# Timeout
# ==========================================================

@pytest.mark.asyncio
async def test_timeout_occurs():
    manager = TimeoutManager(default_timeout=0.05)

    result = await manager.run(slow_operation)

    assert result.success is False
    assert result.output is None
    assert result.timed_out is True
    assert "Execution exceeded timeout" in result.error
    assert result.execution_time >= 0.05


# ==========================================================
# Exception Handling
# ==========================================================

@pytest.mark.asyncio
async def test_timeout_handles_exception():
    manager = TimeoutManager(default_timeout=1)

    result = await manager.run(failing_operation)

    assert result.success is False
    assert result.output is None
    assert result.error == "operation failed"
    assert result.timed_out is False
    assert result.execution_time >= 0


# ==========================================================
# Custom Timeout Override
# ==========================================================

@pytest.mark.asyncio
async def test_timeout_override():
    manager = TimeoutManager(default_timeout=5)

    result = await manager.run(
        slow_operation,
        timeout=0.05,
    )

    assert result.success is False
    assert result.timed_out is True
    assert "0.05" in result.error


# ==========================================================
# Default Timeout Used
# ==========================================================

@pytest.mark.asyncio
async def test_default_timeout_used():
    manager = TimeoutManager(default_timeout=0.3)

    result = await manager.run(slow_operation)

    assert result.success is True
    assert result.output == "finished"
    assert result.timed_out is False


# ==========================================================
# Execution Time Recorded
# ==========================================================

@pytest.mark.asyncio
async def test_execution_time_recorded():
    manager = TimeoutManager(default_timeout=1)

    result = await manager.run(slow_operation)

    assert result.execution_time > 0
    assert isinstance(result.execution_time, float)


# ==========================================================
# Result Metadata
# ==========================================================

@pytest.mark.asyncio
async def test_timeout_result_metadata():
    manager = TimeoutManager(default_timeout=1)

    result = await manager.run(fast_operation)

    assert result.success
    assert result.output == "success"
    assert result.error is None
    assert result.timed_out is False
    assert isinstance(result.execution_time, float)