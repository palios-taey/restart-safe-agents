from __future__ import annotations

from restart_safe_agents.state import BaseTaskState

COMPACTION_PROMPT = (
    "Summarize this work-in-progress into a dense, actionable state summary. "
    "Preserve key decisions, results, and next steps."
)


async def compact_node(
    state: BaseTaskState,
    llm,
    threshold_tokens: int = 12000,
    system_prompt: str = COMPACTION_PROMPT,
) -> BaseTaskState:
    scratchpad = state.get("scratchpad", "")
    token_estimate = len(scratchpad) // 4
    if token_estimate < threshold_tokens:
        state["scratchpad_tokens"] = token_estimate
        return state

    summary = await llm.chat_text(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": scratchpad},
        ],
        max_tokens=2048,
    )
    state["scratchpad"] = f"[COMPACTED STATE]\n{summary}"
    state["scratchpad_tokens"] = len(summary) // 4
    return state
