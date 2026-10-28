"""Redis used strictly as a cache.

Every call reports what happened (`hit`, `miss`, `unavailable`) so the trace can show it.
Redis is never required: any Redis error counts as a miss, is logged once, and Redis is then
skipped for `retry_after_s` seconds, so a dead Redis costs one short timeout, not one per call.
"""

import json
import logging
import time
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

log = logging.getLogger(__name__)


class Cache:
    def __init__(self, client: Redis, retry_after_s: float = 30.0) -> None:
        self._client = client
        self._retry_after_s = retry_after_s
        self._skip_until = 0.0

    def _available(self) -> bool:
        return time.monotonic() >= self._skip_until

    def _mark_down(self, exc: Exception) -> None:
        if self._available():
            log.warning(
                "redis unavailable; continuing without cache",
                extra={"fields": {"error": repr(exc), "retry_after_s": self._retry_after_s}},
            )
        self._skip_until = time.monotonic() + self._retry_after_s

    async def get_json(self, key: str) -> tuple[Any | None, str]:
        if not self._available():
            return None, "unavailable"
        try:
            raw = await self._client.get(key)
        except (RedisError, OSError) as exc:
            self._mark_down(exc)
            return None, "unavailable"
        if raw is None:
            return None, "miss"
        try:
            return json.loads(raw), "hit"
        except ValueError:  # a corrupt or foreign value is a miss, never an error
            log.warning("discarding undecodable cache value", extra={"fields": {"key": key}})
            return None, "miss"

    async def set_json(self, key: str, value: Any, ttl_s: int) -> None:
        if not self._available():
            return
        try:
            await self._client.set(key, json.dumps(value), ex=ttl_s)
        except (RedisError, OSError) as exc:
            self._mark_down(exc)
