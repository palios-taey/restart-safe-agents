from __future__ import annotations

import json

from restart_safe_agents.safety.review_limit import ReviewBounceLimit
from restart_safe_agents.state import BaseTaskState

REVIEW_PROMPT = """Review this deliverable against the original requirements.

Original task: {title}
Requirements: {requirements}

Deliverable:
{artifact}

Score 0.0-1.0 and provide feedback. Respond in JSON:
{{"score": <float>, "feedback": "<specific issues or approved>"}}"""


async def review_node(
    state: BaseTaskState,
    llm,
    review_limit: ReviewBounceLimit | None = None,
    prompt_template: str = REVIEW_PROMPT,
) -> BaseTaskState:
    bounces = state.get("review_bounces", 0)
    if review_limit:
        review_limit.check(state["task_id"], bounces)

    prompt = prompt_template.format(
        title=state["title"],
        requirements=json.dumps(state.get("requirements", [])),
        artifact=state.get("artifact", "[No artifact]"),
    )
    response = await llm.chat_text(
        [{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=512,
    )
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {"score": 0.5, "feedback": "Could not parse review"}

    state["review_score"] = float(result.get("score", 0.5))
    state["review_feedback"] = str(result.get("feedback", ""))
    state["review_bounces"] = bounces + 1
    return state
