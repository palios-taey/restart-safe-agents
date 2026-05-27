# Demo

Run:

```bash
python -m restart_safe_agents.demo
```

Expected behavior:

- ingests one synthetic task
- runs through the checkpointed node flow
- prints the final artifact

The demo uses an in-memory task source and a deterministic mock LLM so it does not require Redis or an external model server.
