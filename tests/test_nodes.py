import fakeredis.aioredis
import pytest

from restart_safe_agents.graph import build_agent
from restart_safe_agents.safety.review_limit import ReviewBounceLimit
from restart_safe_agents.safety.roi_gate import ROIGate
from restart_safe_agents.sources.redis_stream import RedisStreamSource


class MockLLM:
    def __init__(self):
        self.calls = []

    async def chat(self, messages, tools=None, temperature=None, max_tokens=None):
        self.calls.append(("chat", messages[-1]["content"]))
        return {"choices": [{"message": {"content": "artifact body"}}], "usage": {}}

    async def chat_text(self, messages, **kwargs):
        prompt = messages[-1]["content"]
        self.calls.append(("chat_text", prompt))
        if "Classify this task" in prompt:
            return '{"complexity":"complex","estimated_tokens":1200}'
        if "Decompose this complex task" in prompt:
            return '[{"step":1,"action":"draft"},{"step":2,"action":"finalize"}]'
        if "Review this deliverable" in prompt:
            return '{"score":1.0,"feedback":"approved"}'
        if "Summarize this work-in-progress" in messages[0]["content"]:
            return "compacted"
        return "artifact body"

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_agent_happy_path_runs_to_delivery():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    source = RedisStreamSource(redis_client=fake, stream="tasks", consumer_group="workers")
    await source.enqueue(
        {
            "task_id": "task-1",
            "title": "Prepare artifact",
            "description": "Create one artifact",
            "requirements": ["deliver text"],
            "bounty_usd": 10,
        }
    )
    delivered = {}

    def on_artifact(state):
        delivered["artifact"] = state["artifact"]

    agent = build_agent(
        llm=MockLLM(),
        task_source=source,
        roi_gate=ROIGate(min_ratio=0.5),
        review_limit=ReviewBounceLimit(max_bounces=3),
        on_artifact=on_artifact,
    )
    result = await agent.run_once()
    assert result["review_score"] == 1.0
    assert delivered["artifact"] == "artifact body"


@pytest.mark.asyncio
async def test_agent_resumes_from_checkpoint_with_scratchpad_intact():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    source = RedisStreamSource(redis_client=fake, stream="tasks", consumer_group="workers")
    await source.enqueue(
        {
            "task_id": "task-2",
            "title": "Prepare artifact",
            "description": "Create one artifact",
            "requirements": ["deliver text"],
            "bounty_usd": 10,
        }
    )
    llm = MockLLM()
    agent = build_agent(
        llm=llm,
        task_source=source,
        roi_gate=ROIGate(min_ratio=0.5),
        review_limit=ReviewBounceLimit(max_bounces=3),
    )

    payload = await source.claim_next()
    state = {
        "task_id": payload["task_id"],
        "stream_id": payload["stream_id"],
        "title": payload["title"],
        "description": payload["description"],
        "requirements": ["deliver text"],
        "complexity": "complex",
        "plan": [{"step": 1, "action": "draft"}, {"step": 2, "action": "finalize"}],
        "current_step": 1,
        "scratchpad": "partial work survives",
        "review_bounces": 0,
        "escalated": False,
    }
    await source.save_checkpoint(
        "task-2",
        {
            "task_id": "task-2",
            "stream_id": payload["stream_id"],
            "state": state,
            "next_node": "execute",
        },
    )

    result = await agent.run_once()
    assert "partial work survives" in result["scratchpad"]
    assert result["artifact"] == "artifact body"
