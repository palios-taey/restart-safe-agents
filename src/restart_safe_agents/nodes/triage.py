from __future__ import annotations

import json
import logging

from restart_safe_agents.safety.roi_gate import ROIGate
from restart_safe_agents.state import BaseTaskState, TaskComplexity

logger = logging.getLogger("restart_safe_agents.nodes")

TRIAGE_PROMPT = """You are a task appraiser for an autonomous AI agent.
Classify this task and estimate the work required.

Task: {title}
Description: {description}
Bounty: ${bounty_usd}

Respond in JSON:
{{
  "complexity": "simple" | "complex" | "impossible",
  "estimated_tokens": <int>,
  "reasoning": "<1 sentence>"
}}"""


async def triage_node(
    state: BaseTaskState,
    llm,
    roi_gate: ROIGate | None = None,
    prompt_template: str = TRIAGE_PROMPT,
) -> BaseTaskState:
    prompt = prompt_template.format(
        title=state["title"],
        description=state["description"],
        bounty_usd=state.get("bounty_usd", 0),
    )
    response = await llm.chat_text(
        [{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=256,
    )
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        logger.warning("Triage returned non-JSON; defaulting to complex")
        result = {"complexity": "complex", "estimated_tokens": 8000}

    complexity = TaskComplexity(result.get("complexity", "complex"))
    estimated_tokens = int(result.get("estimated_tokens", 8000))
    estimated_cost = roi_gate.evaluate(state, estimated_tokens) if roi_gate else 0.0

    state["complexity"] = complexity
    state["estimated_tokens"] = estimated_tokens
    state["estimated_cost_usd"] = estimated_cost
    return state
