import pytest
from unittest.mock import AsyncMock, patch

from app.orchestration.retry_manager import RetryManager


# ---------------------------------------------------------
# Success immediately
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_success_first_attempt():
    manager = RetryManager(max_retries=3)

    operation = AsyncMock(return_value="success")

    result = await manager.run(operation)

    assert result.success is True
    assert result.output == "success"
    assert result.error is None
    assert result.attempts == 1

    operation.assert_awaited_once()


# ---------------------------------------------------------
# Success after retries
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_success_after_retry():
    manager = RetryManager(
        max_retries=3,
        initial_delay=0,
    )

    operation = AsyncMock(
        side_effect=[
            RuntimeError("temporary"),
            "done",
        ]
    )

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await manager.run(operation)

    assert result.success is True
    assert result.output == "done"
    assert result.attempts == 2
    assert operation.await_count == 2


# ---------------------------------------------------------
# Exhaust retries
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_exhausted():
    manager = RetryManager(
        max_retries=2,
        initial_delay=0,
    )

    operation = AsyncMock(
        side_effect=RuntimeError("network failure")
    )

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await manager.run(operation)

    assert result.success is False
    assert result.output is None
    assert result.error == "network failure"

    # first try + two retries
    assert result.attempts == 3
    assert operation.await_count == 3


# ---------------------------------------------------------
# Retry only specified exceptions
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_only_specific_exception():
    manager = RetryManager(
        max_retries=3,
        initial_delay=0,
    )

    operation = AsyncMock(
        side_effect=ValueError("bad value")
    )

    with pytest.raises(ValueError):
        await manager.run(
            operation,
            retry_exceptions=(RuntimeError,),
        )

    assert operation.await_count == 1


# ---------------------------------------------------------
# Exponential backoff
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_exponential_backoff():
    manager = RetryManager(
        max_retries=3,
        initial_delay=1,
        backoff_factor=2,
    )

    operation = AsyncMock(
        side_effect=[
            RuntimeError(),
            RuntimeError(),
            RuntimeError(),
            "ok",
        ]
    )

    with patch("asyncio.sleep", new_callable=AsyncMock) as sleep_mock:
        result = await manager.run(operation)

    assert result.success is True
    assert result.attempts == 4

    assert sleep_mock.await_args_list[0].args == (1,)
    assert sleep_mock.await_args_list[1].args == (2,)
    assert sleep_mock.await_args_list[2].args == (4,)


# ---------------------------------------------------------
# RetryResult metadata
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_result_metadata():
    manager = RetryManager(
        max_retries=1,
        initial_delay=0,
    )

    operation = AsyncMock(return_value={"status": "ok"})

    result = await manager.run(operation)

    assert result.success
    assert result.output == {"status": "ok"}
    assert result.error is None
    assert result.attempts == 1