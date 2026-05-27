from __future__ import annotations

import json

from restart_safe_agents.state import BaseTaskState

PLAN_PROMPT = """You are a task planner. Decompose this complex task into ordered sub-steps.

Task: {title}
Description: {description}
Requirements: {requirements}

Respond with a JSON array of steps:
[{{"step": 1, "action": "<what to do>", "tool": "<tool_name or null>"}}]"""


async def plan_node(
    state: BaseTaskState,
    llm,
    prompt_template: str = PLAN_PROMPT,
) -> BaseTaskState:
    prompt = prompt_template.format(
        title=state["title"],
        description=state["description"],
        requirements=json.dumps(state.get("requirements", [])),
    )
    response = await llm.chat_text(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )
    try:
        plan = json.loads(response)
    except json.JSONDecodeError:
        plan = [{"step": 1, "action": state["description"], "tool": None}]

    state["plan"] = plan
    state["current_step"] = 0
    return state
