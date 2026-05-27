from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"
    IMPOSSIBLE = "impossible"


class BaseTaskState(TypedDict, total=False):
    task_id: str
    stream_id: str
    title: str
    description: str
    requirements: list[str]
    complexity: TaskComplexity
    estimated_tokens: int
    estimated_cost_usd: float
    plan: list[dict[str, Any]]
    current_step: int
    scratchpad: str
    scratchpad_tokens: int
    tool_results: list[dict[str, Any]]
    artifact: str
    review_score: float
    review_feedback: str
    review_bounces: int
    error: str | None
    escalated: bool
