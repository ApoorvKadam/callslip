"""Liveness and readiness.

`/api/health` answers if the process is up (used by the container health check).
`/api/ready` checks dependencies: PostgreSQL is required (503 without it); Redis is optional,
so its loss reports `degraded` but stays 200, because the app keeps working without its cache.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from app.api.deps import get_pool, get_redis

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready(
    response: Response,
    pool: Annotated[AsyncConnectionPool, Depends(get_pool)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> dict:
    checks: dict[str, str] = {}
    try:
        async with pool.connection(timeout=2) as conn:
            await conn.execute("SELECT 1")
        checks["database"] = "up"
    except Exception:  # any failure means not ready
        checks["database"] = "down"
    try:
        await redis.ping()
        checks["redis"] = "up"
    except Exception:  # Redis is a cache: losing it degrades, it does not stop the app
        checks["redis"] = "down"

    if checks["database"] == "down":
        response.status_code = 503
        status = "unavailable"
    else:
        status = "ok" if checks["redis"] == "up" else "degraded"
    return {"status": status, "checks": checks}
