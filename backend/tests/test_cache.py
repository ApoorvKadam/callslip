"""The cache wrapper against a real Redis, and against an address where nothing listens."""

import os
import time

import pytest
from redis.asyncio import Redis

from app.cache import Cache

TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL")


@pytest.mark.skipif(not TEST_REDIS_URL, reason="TEST_REDIS_URL is not set")
async def test_round_trip_and_miss():
    client = Redis.from_url(TEST_REDIS_URL)
    cache = Cache(client)
    key = f"test:{time.time_ns()}"
    assert await cache.get_json(key) == (None, "miss")
    await cache.set_json(key, {"hits": [1, 2]}, ttl_s=30)
    assert await cache.get_json(key) == ({"hits": [1, 2]}, "hit")
    assert 0 < await client.ttl(key) <= 30
    await client.aclose()


async def test_unreachable_redis_is_a_miss_and_is_skipped_for_a_while():
    # Port 1 on localhost: connection refused immediately.
    client = Redis.from_url("redis://127.0.0.1:1/0", socket_timeout=0.2, socket_connect_timeout=0.2)
    cache = Cache(client, retry_after_s=60)
    assert await cache.get_json("k") == (None, "unavailable")
    # Within the skip window Redis is not even tried, so this returns at once.
    started = time.monotonic()
    assert await cache.get_json("k") == (None, "unavailable")
    await cache.set_json("k", {"x": 1}, ttl_s=5)
    assert time.monotonic() - started < 0.05
    await client.aclose()
