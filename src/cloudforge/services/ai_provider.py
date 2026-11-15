import asyncio
from typing import Awaitable, TypeVar
import random
from collections.abc import  Callable

T = TypeVar("T")


class AIProviderTemporaryError(Exception):
    """A transient provider failure that may be retried."""


class AIProviderTimeoutError(AIProviderTemporaryError):
    """A provider call exceeded its time budget (retryable)."""


async def execute_with_timeout(
    operation: Callable[[], Awaitable[T]],
    timeout_seconds: float,
) -> T:
    """
    Run one provider call with a hard time limit.

    The underlying task is cancelled when the limit is reached.
    """

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    try:
        return await asyncio.wait_for(
            operation(),
            timeout=timeout_seconds,
        )
    except TimeoutError as exc:
        raise AIProviderTimeoutError(
            f"AI provider call exceeded {timeout_seconds} seconds"
        ) from exc


async def execute_with_retry(
    operation: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
) -> T:
    """
    Retry transient AI provider failures.

    Each attempt creates a fresh awaitable.
    Uses bounded exponential backoff with full jitter.
    """

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    if base_delay < 0 or max_delay < 0:
        raise ValueError("Retry delays cannot be negative")

    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()

        except AIProviderTemporaryError:
            if attempt == max_attempts:
                raise

            # Exponential backoff, capped at max_delay.
            delay_cap = min(
                max_delay,
                base_delay * (2 ** (attempt - 1)),
            )

            # Full jitter distributes retry traffic.
            delay = random.uniform(0, delay_cap)

            await asyncio.sleep(delay)

    raise RuntimeError("Unreachable retry state")
