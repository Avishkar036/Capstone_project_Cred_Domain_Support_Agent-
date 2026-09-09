"""Timeout and retry helpers with deterministic demonstrations."""

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")
MAX_ATTEMPTS = 4
INITIAL_INTERVAL = 0.01
MAX_INTERVAL = 0.05
JITTER = 0.0
NODE_TIMEOUT_SECONDS = 0.05
GLOBAL_TIMEOUT_SECONDS = 0.2


async def retry_with_backoff(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = MAX_ATTEMPTS,
    initial_interval: float = INITIAL_INTERVAL,
    max_interval: float = MAX_INTERVAL,
    jitter: float = JITTER,
) -> T:
    """Retry transient failures with capped exponential backoff and jitter."""
    for attempt in range(max_attempts):
        try:
            return await operation()
        except Exception:
            if attempt == max_attempts - 1:
                raise
            delay = min(max_interval, initial_interval * (2**attempt))
            if jitter:
                delay += random.uniform(0, jitter)
            await asyncio.sleep(delay)
    raise RuntimeError("unreachable")


async def run_with_timeouts(
    node: Callable[[], Awaitable[T]],
    *,
    node_timeout: float = NODE_TIMEOUT_SECONDS,
    global_timeout: float = GLOBAL_TIMEOUT_SECONDS,
) -> T:
    """Apply a per-node timeout inside a global whole-run timeout."""
    async def run_node() -> T:
        return await asyncio.wait_for(node(), timeout=node_timeout)

    return await asyncio.wait_for(run_node(), timeout=global_timeout)


async def transient_demo() -> tuple[str, int]:
    """Fail twice, then succeed through the configured retry policy."""
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("simulated transient failure")
        return "recovered"

    return await retry_with_backoff(operation), attempts


async def node_timeout_demo() -> None:
    async def slow_node() -> None:
        await asyncio.sleep(0.2)

    await run_with_timeouts(slow_node, node_timeout=0.01, global_timeout=0.1)


async def global_timeout_demo() -> None:
    async def long_run() -> None:
        await asyncio.sleep(0.2)

    await run_with_timeouts(long_run, node_timeout=1.0, global_timeout=0.01)


if __name__ == "__main__":
    print("Retry demo:", asyncio.run(transient_demo()))
    for label, demo in (("Node timeout", node_timeout_demo), ("Global timeout", global_timeout_demo)):
        try:
            asyncio.run(demo())
        except asyncio.TimeoutError:
            print(f"{label}: clean timeout")
