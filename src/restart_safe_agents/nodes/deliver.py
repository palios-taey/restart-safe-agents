from __future__ import annotations

from typing import Awaitable, Callable

from restart_safe_agents.state import BaseTaskState


async def deliver_node(
    state: BaseTaskState,
    on_artifact: Callable[[BaseTaskState], Awaitable[None] | None] | None = None,
) -> BaseTaskState:
    if on_artifact:
        maybe_awaitable = on_artifact(state)
        if maybe_awaitable is not None and hasattr(maybe_awaitable, "__await__"):
            await maybe_awaitable
    return state
