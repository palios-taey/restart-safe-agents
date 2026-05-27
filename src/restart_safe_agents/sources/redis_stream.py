from __future__ import annotations

import json
import uuid
from typing import Any

import redis.asyncio as aioredis


class RedisStreamSource:
    def __init__(
        self,
        url: str = "redis://127.0.0.1:6379/0",
        stream: str = "tasks:inbox",
        consumer_group: str = "restart-safe-agents",
        consumer_name: str | None = None,
        checkpoint_prefix: str = "restart_safe_agents:checkpoint",
        redis_client: aioredis.Redis | None = None,
    ):
        self.url = url
        self.stream = stream
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name or f"worker-{uuid.uuid4().hex[:8]}"
        self.checkpoint_prefix = checkpoint_prefix
        self._redis = redis_client

    async def connect(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.url, decode_responses=True)
        try:
            await self._redis.xgroup_create(self.stream, self.consumer_group, id="0", mkstream=True)
        except aioredis.ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise
        return self._redis

    def _checkpoint_key(self, task_id: str) -> str:
        return f"{self.checkpoint_prefix}:{task_id}"

    @property
    def _inflight_key(self) -> str:
        return f"{self.checkpoint_prefix}:inflight"

    async def enqueue(self, payload: dict[str, Any]) -> str:
        redis = await self.connect()
        data = {
            key: json.dumps(value) if isinstance(value, (list, dict)) else str(value)
            for key, value in payload.items()
        }
        return await redis.xadd(self.stream, data)

    async def claim_next(self) -> dict[str, Any] | None:
        redis = await self.connect()
        messages = await redis.xreadgroup(
            self.consumer_group,
            self.consumer_name,
            {self.stream: ">"},
            count=1,
            block=100,
        )
        if not messages:
            return None
        _, entries = messages[0]
        stream_id, payload = entries[0]
        task = dict(payload)
        task["stream_id"] = stream_id
        return task

    async def ack(self, task_id: str, stream_id: str | None = None) -> None:
        redis = await self.connect()
        checkpoint = None
        if stream_id is None:
            checkpoint = await self.load_checkpoint(task_id)
            stream_id = checkpoint.get("stream_id") if checkpoint else None
        if stream_id:
            await redis.xack(self.stream, self.consumer_group, stream_id)
        await self.clear_checkpoint(task_id)

    async def save_checkpoint(self, task_id: str, checkpoint: dict[str, Any]) -> None:
        redis = await self.connect()
        pipe = redis.pipeline()
        pipe.set(self._checkpoint_key(task_id), json.dumps(checkpoint))
        pipe.sadd(self._inflight_key, task_id)
        await pipe.execute()

    async def load_checkpoint(self, task_id: str) -> dict[str, Any] | None:
        redis = await self.connect()
        data = await redis.get(self._checkpoint_key(task_id))
        return json.loads(data) if data else None

    async def clear_checkpoint(self, task_id: str) -> None:
        redis = await self.connect()
        pipe = redis.pipeline()
        pipe.delete(self._checkpoint_key(task_id))
        pipe.srem(self._inflight_key, task_id)
        await pipe.execute()

    async def list_inflight(self) -> list[str]:
        redis = await self.connect()
        members = await redis.smembers(self._inflight_key)
        return sorted(members)

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
