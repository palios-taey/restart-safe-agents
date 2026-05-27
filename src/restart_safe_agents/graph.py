from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from restart_safe_agents.exceptions import EscalationError
from restart_safe_agents.nodes import (
    compact_node,
    deliver_node,
    execute_node,
    plan_node,
    review_node,
    triage_node,
)
from restart_safe_agents.safety.review_limit import ReviewBounceLimit
from restart_safe_agents.safety.roi_gate import ROIGate
from restart_safe_agents.state import BaseTaskState, TaskComplexity

StateFactory = Callable[[dict[str, Any]], BaseTaskState]


def default_state_factory(payload: dict[str, Any]) -> BaseTaskState:
    requirements = payload.get("requirements", [])
    if isinstance(requirements, str):
        try:
            requirements = json.loads(requirements)
        except json.JSONDecodeError:
            requirements = [requirements]
    return {
        "task_id": payload.get("task_id", payload.get("stream_id", "")),
        "stream_id": payload.get("stream_id", ""),
        "title": payload.get("title", ""),
        "description": payload.get("description", ""),
        "requirements": requirements,
        "review_bounces": 0,
        "escalated": False,
    }


@dataclass
class NodeRegistry:
    triage: Callable[..., Awaitable[BaseTaskState]] = triage_node
    plan: Callable[..., Awaitable[BaseTaskState]] = plan_node
    execute: Callable[..., Awaitable[BaseTaskState]] = execute_node
    compact: Callable[..., Awaitable[BaseTaskState]] = compact_node
    review: Callable[..., Awaitable[BaseTaskState]] = review_node
    deliver: Callable[..., Awaitable[BaseTaskState]] = deliver_node


@dataclass
class RestartSafeAgent:
    llm: Any
    task_source: Any
    nodes: NodeRegistry = field(default_factory=NodeRegistry)
    state_factory: StateFactory = default_state_factory
    tool_registry: dict[str, Any] | None = None
    roi_gate: ROIGate | None = None
    review_limit: ReviewBounceLimit | None = None
    compaction_threshold: int = 12_000
    review_pass_threshold: float = 0.90
    on_artifact: Callable[[BaseTaskState], Awaitable[None] | None] | None = None

    async def _checkpoint(self, state: BaseTaskState, next_node: str) -> None:
        await self.task_source.save_checkpoint(
            state["task_id"],
            {
                "task_id": state["task_id"],
                "stream_id": state.get("stream_id"),
                "state": state,
                "next_node": next_node,
            },
        )

    async def _claim_or_resume(self) -> tuple[BaseTaskState, str] | tuple[None, None]:
        inflight = await self.task_source.list_inflight()
        if inflight:
            checkpoint = await self.task_source.load_checkpoint(inflight[0])
            if checkpoint:
                return checkpoint["state"], checkpoint["next_node"]

        payload = await self.task_source.claim_next()
        if payload is None:
            return None, None
        state = self.state_factory(payload)
        await self._checkpoint(state, "triage")
        return state, "triage"

    async def run_once(self) -> BaseTaskState | None:
        state, next_node = await self._claim_or_resume()
        if state is None:
            return None

        while True:
            if next_node == "triage":
                state = await self.nodes.triage(state, self.llm, roi_gate=self.roi_gate)
                complexity = TaskComplexity(state["complexity"])
                if complexity == TaskComplexity.IMPOSSIBLE:
                    raise EscalationError(state["task_id"], "Task classified as impossible")
                next_node = "plan" if complexity == TaskComplexity.COMPLEX else "execute"
                await self._checkpoint(state, next_node)
                continue

            if next_node == "plan":
                state = await self.nodes.plan(state, self.llm)
                next_node = "execute"
                await self._checkpoint(state, next_node)
                continue

            if next_node == "execute":
                state = await self.nodes.execute(state, self.llm, tool_registry=self.tool_registry)
                next_node = "compact"
                await self._checkpoint(state, next_node)
                continue

            if next_node == "compact":
                state = await self.nodes.compact(
                    state,
                    self.llm,
                    threshold_tokens=self.compaction_threshold,
                )
                complexity = TaskComplexity(state["complexity"])
                if complexity == TaskComplexity.COMPLEX and state.get("current_step", 0) < len(state.get("plan", [])):
                    next_node = "execute"
                else:
                    next_node = "review"
                await self._checkpoint(state, next_node)
                continue

            if next_node == "review":
                state = await self.nodes.review(state, self.llm, review_limit=self.review_limit)
                if state.get("review_score", 0.0) < self.review_pass_threshold:
                    next_node = "execute"
                else:
                    next_node = "deliver"
                await self._checkpoint(state, next_node)
                continue

            if next_node == "deliver":
                state = await self.nodes.deliver(state, on_artifact=self.on_artifact)
                await self.task_source.ack(state["task_id"], state.get("stream_id"))
                return state

            raise RuntimeError(f"Unknown node: {next_node}")

    async def run_forever(self, poll_interval: float = 1.0) -> None:
        while True:
            result = await self.run_once()
            if result is None:
                await asyncio.sleep(poll_interval)

    def run(self, poll_interval: float = 1.0) -> None:
        asyncio.run(self.run_forever(poll_interval=poll_interval))


def build_agent(**kwargs: Any) -> RestartSafeAgent:
    return RestartSafeAgent(**kwargs)
