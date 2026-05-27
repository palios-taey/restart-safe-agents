import fakeredis.aioredis
import pytest

from restart_safe_agents.sources.redis_stream import RedisStreamSource


@pytest.mark.asyncio
async def test_redis_source_checkpoint_roundtrip():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    source = RedisStreamSource(redis_client=fake, stream="test:stream", consumer_group="testers")
    await source.enqueue({"task_id": "job-1", "title": "hello"})
    payload = await source.claim_next()
    assert payload["task_id"] == "job-1"

    await source.save_checkpoint("job-1", {"task_id": "job-1", "state": {"scratchpad": "abc"}, "next_node": "review"})
    checkpoint = await source.load_checkpoint("job-1")
    assert checkpoint["state"]["scratchpad"] == "abc"
    assert await source.list_inflight() == ["job-1"]

    await source.ack("job-1", payload["stream_id"])
    assert await source.list_inflight() == []
