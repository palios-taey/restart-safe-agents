# restart-safe-agents

Restart-safe agent execution with explicit node checkpoints, Redis Streams ingestion, and bounded review / ROI safety policies.

## What It Solves

Long-running agents fail in boring ways: a process restarts, context gets compacted badly, or a review loop spins forever. This library keeps the execution graph small and explicit:

- `triage -> plan -> execute -> compact -> review -> deliver`
- checkpoint after every successful node
- resume from the next node after a restart
- preserve scratchpad state across restarts

## Scope

Included:

- generic task state spine
- checkpointed runner
- Redis Streams task source
- OpenAI-compatible async LLM client
- ROI gate and review-bounce limiter
- overridable node registry

Not included:

- your tool implementations
- your domain-specific task fields
- your deployment automation

## Install

```bash
pip install restart-safe-agents
```

For local development:

```bash
make install
```

## Quickstart

```python
from restart_safe_agents import (
    OpenAILLMClient,
    RedisStreamSource,
    ROIGate,
    ReviewBounceLimit,
    build_agent,
)

llm = OpenAILLMClient(
    api_url="http://localhost:8000/v1",
    model="Qwen/Qwen3.5-27B",
)

source = RedisStreamSource(
    url="redis://localhost:6379/0",
    stream="tasks:inbox",
    consumer_group="restart-safe-agents",
)

agent = build_agent(
    llm=llm,
    task_source=source,
    roi_gate=ROIGate(min_ratio=0.5),
    review_limit=ReviewBounceLimit(max_bounces=4),
)
```

Run the bundled synthetic demo:

```bash
python -m restart_safe_agents.demo
```

## Restart-Safety Contract

Three-register truth:

- `[Observed]` The included tests cover checkpoint-resume using a persisted source with scratchpad continuity.
- `[Observed]` The bundled demo completes a synthetic task end-to-end and prints the final artifact.
- `[Inferred]` This extraction pattern is suitable for other OpenAI-compatible agent stacks because the state spine and task source are generic.
- `[Unknown]` Production fleet uptime, restart counts, and long-run delivery rates are not published here because this repo does not yet include a measured public telemetry report.

Behavior:

1. A task is claimed from the source.
2. The runner writes a checkpoint before entering the next node.
3. A successful node writes a new checkpoint with the next node pointer.
4. If the process dies mid-node, the previous checkpoint remains authoritative.
5. On restart, the runner resumes from the saved checkpoint with scratchpad intact.

## Treasurer Extraction Notes

This repo was extracted from Treasurer's agent core. Treasurer-specific fields such as `platform`, `bounty_usd`, `revenue_usd`, and `delivered` stay outside the public library in Treasurer's own state subclass.

## Development

```bash
make test
make demo
```

## License

MIT.
