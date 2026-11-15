"""Unit tests for AI provider timeout and retry wrappers."""

import asyncio

import pytest

from cloudforge.services import ai_provider
from cloudforge.services.ai_provider import (
    AIProviderTemporaryError,
    AIProviderTimeoutError,
    execute_with_retry,
    execute_with_timeout,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def recorded_sleeps(monkeypatch):
    """Skip real backoff sleeps and record requested delays."""

    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(ai_provider.asyncio, "sleep", fake_sleep)
    # Jitter returns the cap so backoff values are deterministic.
    monkeypatch.setattr(ai_provider.random, "uniform", lambda low, high: high)
    return delays


class FlakyOperation:
    """Fails with the given errors in order, then succeeds."""

    def __init__(self, errors, result="ok"):
        self.errors = list(errors)
        self.result = result
        self.calls = 0

    async def __call__(self):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return self.result


# ----------------------------------------------------------- timeout


def test_timeout_returns_result_when_fast():
    async def fast():
        return "done"

    assert asyncio.run(execute_with_timeout(fast, timeout_seconds=1)) == "done"


def test_timeout_raises_provider_timeout_error():
    cancelled = asyncio.Event()

    async def slow():
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    async def run():
        with pytest.raises(AIProviderTimeoutError):
            await execute_with_timeout(slow, timeout_seconds=0.05)
        # The slow call is cancelled, not left running.
        assert cancelled.is_set()

    asyncio.run(run())


def test_timeout_error_is_retryable_type():
    assert issubclass(AIProviderTimeoutError, AIProviderTemporaryError)


def test_timeout_propagates_operation_errors():
    async def broken():
        raise KeyError("bad response")

    with pytest.raises(KeyError):
        asyncio.run(execute_with_timeout(broken, timeout_seconds=1))


@pytest.mark.parametrize("bad", [0, -1])
def test_timeout_rejects_non_positive_values(bad):
    async def op():
        return None

    with pytest.raises(ValueError):
        asyncio.run(execute_with_timeout(op, timeout_seconds=bad))


# ------------------------------------------------------------- retry


def test_retry_succeeds_first_attempt(recorded_sleeps):
    op = FlakyOperation([])

    assert asyncio.run(execute_with_retry(op)) == "ok"
    assert op.calls == 1
    assert recorded_sleeps == []


def test_retry_recovers_from_transient_errors(recorded_sleeps):
    op = FlakyOperation([AIProviderTemporaryError(), AIProviderTemporaryError()])

    result = asyncio.run(
        execute_with_retry(op, max_attempts=3, base_delay=0.1, max_delay=2.0)
    )

    assert result == "ok"
    assert op.calls == 3
    # Exponential backoff: 0.1, 0.2.
    assert recorded_sleeps == pytest.approx([0.1, 0.2])


def test_retry_backoff_is_capped(recorded_sleeps):
    op = FlakyOperation([AIProviderTemporaryError()] * 5)

    asyncio.run(execute_with_retry(op, max_attempts=6, base_delay=1.0, max_delay=3.0))

    assert recorded_sleeps == pytest.approx([1.0, 2.0, 3.0, 3.0, 3.0])


def test_retry_jitter_stays_within_cap(monkeypatch):
    bounds: list[tuple[float, float]] = []

    async def fake_sleep(delay):
        return None

    def fake_uniform(low, high):
        bounds.append((low, high))
        return low

    monkeypatch.setattr(ai_provider.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(ai_provider.random, "uniform", fake_uniform)

    op = FlakyOperation([AIProviderTemporaryError()] * 2)
    asyncio.run(execute_with_retry(op, max_attempts=3, base_delay=0.5))

    # Full jitter: uniform(0, cap) for each backoff.
    assert bounds == [(0, 0.5), (0, 1.0)]


def test_retry_exhaustion_reraises_last_error(recorded_sleeps):
    last = AIProviderTemporaryError("third failure")
    op = FlakyOperation(
        [AIProviderTemporaryError("1"), AIProviderTemporaryError("2"), last]
    )

    with pytest.raises(AIProviderTemporaryError) as exc_info:
        asyncio.run(execute_with_retry(op, max_attempts=3))

    assert exc_info.value is last
    assert op.calls == 3
    # No sleep after the final attempt.
    assert len(recorded_sleeps) == 2


def test_non_retryable_error_is_not_retried(recorded_sleeps):
    op = FlakyOperation([ValueError("invalid request")])

    with pytest.raises(ValueError):
        asyncio.run(execute_with_retry(op, max_attempts=5))

    assert op.calls == 1
    assert recorded_sleeps == []


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"base_delay": -0.1},
        {"max_delay": -1},
    ],
)
def test_retry_rejects_invalid_configuration(kwargs):
    op = FlakyOperation([])

    with pytest.raises(ValueError):
        asyncio.run(execute_with_retry(op, **kwargs))

    assert op.calls == 0


def test_timeout_composes_with_retry(recorded_sleeps):
    calls = 0

    async def always_slow():
        nonlocal calls
        calls += 1
        # Real event-loop wait; the patched sleep only affects
        # the retry module's backoff, so use an Event instead.
        await asyncio.Event().wait()

    async def attempt():
        return await execute_with_timeout(always_slow, timeout_seconds=0.02)

    with pytest.raises(AIProviderTimeoutError):
        asyncio.run(execute_with_retry(attempt, max_attempts=3))

    assert calls == 3
    assert len(recorded_sleeps) == 2


def test_timeout_then_success_with_retry(recorded_sleeps):
    calls = 0

    async def slow_then_fast():
        nonlocal calls
        calls += 1
        if calls == 1:
            await asyncio.Event().wait()
        return "recovered"

    async def attempt():
        return await execute_with_timeout(slow_then_fast, timeout_seconds=0.02)

    assert asyncio.run(execute_with_retry(attempt, max_attempts=3)) == "recovered"
    assert calls == 2
