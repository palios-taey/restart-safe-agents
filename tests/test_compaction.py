import pytest

from restart_safe_agents.nodes.compact import compact_node


class CompactingLLM:
    async def chat_text(self, messages, **kwargs):
        return "short summary"


@pytest.mark.asyncio
async def test_compaction_replaces_large_scratchpad():
    state = {"task_id": "t1", "scratchpad": "x" * 200, "complexity": "simple"}
    result = await compact_node(state, CompactingLLM(), threshold_tokens=10)
    assert result["scratchpad"].startswith("[COMPACTED STATE]")
    assert result["scratchpad_tokens"] > 0
