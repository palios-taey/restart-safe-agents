from __future__ import annotations

from dataclasses import dataclass

from restart_safe_agents.exceptions import MarginCallError
from restart_safe_agents.state import BaseTaskState


@dataclass
class ROIGate:
    min_ratio: float = 0.5
    tokens_per_dollar: float = 500_000.0

    def evaluate(self, state: BaseTaskState, estimated_tokens: int) -> float:
        estimated_cost = estimated_tokens / self.tokens_per_dollar
        bounty = float(state.get("bounty_usd", 0.0))  # app-specific field if present
        if bounty > 0 and estimated_cost > bounty * self.min_ratio:
            raise MarginCallError(
                state["task_id"],
                estimated_cost,
                bounty * self.min_ratio,
            )
        return estimated_cost
