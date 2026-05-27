from __future__ import annotations

import json
from typing import Any

from restart_safe_agents.state import BaseTaskState, TaskComplexity

SYSTEM_PROMPT = "You are an autonomous agent completing tasks. Be precise and efficient."


async def execute_node(
    state: BaseTaskState,
    llm,
    tool_registry: dict[str, Any] | None = None,
    system_prompt: str = SYSTEM_PROMPT,
) -> BaseTaskState:
    complexity = TaskComplexity(state["complexity"])
    if complexity == TaskComplexity.SIMPLE:
        exec_prompt = f"Complete this task:\n{state['description']}"
    else:
        step = state["plan"][state["current_step"]]
        exec_prompt = f"Execute step {step['step']}: {step['action']}"
        if state.get("scratchpad"):
            exec_prompt += f"\n\nPrevious work:\n{state['scratchpad']}"

    tools = None
    if tool_registry:
        tools = [{"type": "function", "function": spec} for spec in tool_registry.values()]

    response = await llm.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": exec_prompt},
        ],
        tools=tools,
    )
    choice = response["choices"][0]["message"]
    if choice.get("tool_calls"):
        tool_results = []
        for call in choice["tool_calls"]:
            fn_name = call["function"]["name"]
            fn_args = json.loads(call["function"]["arguments"])
            result = {"tool": fn_name, "args": fn_args, "result": "[Tool execution pending]"}
            tool_results.append(result)
        state.setdefault("tool_results", []).extend(tool_results)
        state["scratchpad"] = (
            state.get("scratchpad", "") + f"\n\nStep result: {json.dumps(tool_results, indent=2)}"
        ).strip()
    else:
        content = choice.get("content", "")
        state["scratchpad"] = (state.get("scratchpad", "") + f"\n\nStep result: {content}").strip()
        state["artifact"] = content

    if complexity == TaskComplexity.COMPLEX:
        state["current_step"] = state.get("current_step", 0) + 1
    return state
