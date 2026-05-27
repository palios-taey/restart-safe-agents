from __future__ import annotations

from dataclasses import dataclass

from restart_safe_agents.exceptions import ReviewLoopError


@dataclass
class ReviewBounceLimit:
    max_bounces: int = 4

    def check(self, task_id: str, bounces: int) -> None:
        if bounces >= self.max_bounces:
            raise ReviewLoopError(task_id, bounces)
