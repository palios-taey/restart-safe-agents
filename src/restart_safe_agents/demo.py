from __future__ import annotations

import asyncio
import json

from restart_safe_agents.graph import build_agent
from restart_safe_agents.safety.review_limit import ReviewBounceLimit
from restart_safe_agents.safety.roi_gate import ROIGate


class DemoLLM:
    async def chat(self, messages, tools=None, temperature=None, max_tokens=None):
        prompt = messages[-1]["content"]
        if "Execute step" in prompt:
            content = "Wrote the synthetic artifact body."
        else:
            content = "Completed the synthetic task."
        return {"choices": [{"message": {"content": content}}], "usage": {}}

    async def chat_text(self, messages, **kwargs):
        prompt = messages[-1]["content"]
        if "Classify this task" in prompt:
            return json.dumps({"complexity": "simple", "estimated_tokens": 1200})
        if "Decompose this complex task" in prompt:
            return json.dumps([{"step": 1, "action": "Write the artifact", "tool": None}])
        if "Review this deliverable" in prompt:
            return json.dumps({"score": 1.0, "feedback": "approved"})
        if "Summarize this work-in-progress" in messages[0]["content"]:
            return "Compacted scratchpad."
        return "Completed the synthetic task."

    async def close(self):
        return None


class MemorySource:
    def __init__(self):
        self.queue = []
        self.checkpoints = {}
        self.inflight = set()

    async def enqueue(self, payload):
        self.queue.append(payload)

    async def claim_next(self):
        if not self.queue:
            return None
        payload = self.queue.pop(0)
        payload.setdefault("stream_id", f"memory-{len(self.checkpoints)+1}")
        return payload

    async def ack(self, task_id, stream_id=None):
        self.checkpoints.pop(task_id, None)
        self.inflight.discard(task_id)

    async def save_checkpoint(self, task_id, checkpoint):
        self.checkpoints[task_id] = checkpoint
        self.inflight.add(task_id)

    async def load_checkpoint(self, task_id):
        return self.checkpoints.get(task_id)

    async def clear_checkpoint(self, task_id):
        self.checkpoints.pop(task_id, None)
        self.inflight.discard(task_id)

    async def list_inflight(self):
        return sorted(self.inflight)

    async def close(self):
        return None


async def main() -> None:
    source = MemorySource()
    await source.enqueue(
        {
            "task_id": "demo-1",
            "title": "Write synthetic artifact",
            "description": "Produce one short artifact proving the DAG works.",
            "requirements": ["artifact must mention restart safety"],
        }
    )

    final_artifact = {}

    def on_artifact(state):
        final_artifact["artifact"] = state.get("artifact", "")

    agent = build_agent(
        llm=DemoLLM(),
        task_source=source,
        roi_gate=ROIGate(min_ratio=0.5),
        review_limit=ReviewBounceLimit(max_bounces=3),
        on_artifact=on_artifact,
    )
    state = await agent.run_once()
    print(f"task_id={state['task_id']}")
    print(f"review_score={state['review_score']}")
    print(f"artifact={final_artifact['artifact']}")


if __name__ == "__main__":
    asyncio.run(main())
