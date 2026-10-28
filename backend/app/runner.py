"""Run worker: executes the questions the API queues. `python -m app.runner`.

The API records a run's work (start, or resume after a clarification) and returns at once; it
holds no run state, so it can run as several replicas. This process claims queued runs with a
lease (see runs/queue.py), runs up to `run_concurrency` of them at a time, renews the leases
while they execute, and closes runs whose worker disappeared. Run workers scale by count.
"""

import asyncio
import contextlib
import logging
import os
import signal
import socket
import time
from collections.abc import Coroutine
from pathlib import Path

import psycopg
from anthropic import AsyncAnthropic
from psycopg_pool import PoolTimeout
from redis.asyncio import Redis

from app.agent.baseline import run_baseline
from app.agent.loop import resume_agent, start_agent
from app.cache import Cache
from app.config import Settings, get_settings
from app.db import migrate, open_pool
from app.embeddings import Embedder
from app.llm import LLM
from app.logs import setup_logging
from app.retrieval.search import SearchService
from app.runs import queue
from app.runs.context import RunContext
from app.runs.manager import RunManager
from app.runs.store import RunStore

log = logging.getLogger("app.runner")
TRANSIENT_DB_ERRORS = (psycopg.OperationalError, PoolTimeout, OSError)
HEARTBEAT = Path("/tmp/runner-heartbeat")


async def first_event_then(ctx: RunContext, type_: str, data: dict, work: Coroutine) -> None:
    """Write a run's first event inside its task. A failed write then closes the run as failed,
    like any other error, instead of leaving it marked running with nothing executing it."""
    try:
        await ctx.emit(type_, data)
    except BaseException:
        work.close()
        raise
    await work


async def execution(row: dict, store, llm, search, settings: Settings) -> None:
    """Carry out one claimed run. Everything happens inside the run's task, so any error here,
    even in setting the run up, closes that run as failed and leaves the others alone."""
    ctx = RunContext(row["id"], row["session_id"], store, llm, search, settings)
    ctx.viewer = row["user_id"]
    faults = dict(row["faults"] or {})
    data = row["work_data"] or {}
    if row["work"] == "resume":
        # Waiting for the user does not count against the run's time budget.
        ctx.started = time.monotonic() - row["exec_ms"] / 1000
        ctx.model_turns, ctx.tool_calls = row["model_turns"], row["tool_calls"]
        work = resume_agent(ctx, faults)
        await first_event_then(ctx, "clarification_answered", data.get("event", {}), work)
        return
    history = [tuple(turn) for turn in data.get("history", [])]
    if row["mode"] == "agent":
        work = start_agent(ctx, row["question"], history, faults)
    else:
        work = run_baseline(ctx, row["question"], history, faults)
    await first_event_then(ctx, "run_started", data.get("event", {}), work)


async def heartbeat(stop: asyncio.Event, every_s: float = 10.0) -> None:
    while not stop.is_set():
        HEARTBEAT.touch()
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=every_s)


async def run() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    owner = f"{socket.gethostname()}:{os.getpid()}"
    await migrate(settings.database_url)
    pool = await open_pool(settings.database_url, max_size=settings.run_concurrency + 2)
    redis = Redis.from_url(settings.redis_url, socket_timeout=0.25, socket_connect_timeout=0.25)
    embedder = await asyncio.to_thread(
        Embedder,
        settings.embed_model,
        settings.fastembed_cache_path,
        settings.embed_threads,
        settings.embed_batch_size,
    )
    search = SearchService(pool, embedder, Cache(redis))
    store = RunStore(pool)
    # Without a key the API refuses questions, so nothing is queued and this stays idle.
    llm = (
        LLM(
            AsyncAnthropic(api_key=settings.anthropic_api_key, max_retries=2),
            pool,
            settings.answer_model,
            settings.answer_effort,
        )
        if settings.anthropic_api_key
        else None
    )
    manager = RunManager(store)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    log.info("run worker started", extra={"fields": {"owner": owner}})
    beat = asyncio.create_task(heartbeat(stop))
    renewed = time.monotonic()

    while not stop.is_set():
        try:
            async with pool.connection() as conn:
                if time.monotonic() - renewed >= settings.run_lease_seconds / 4:
                    await queue.renew(conn, owner, list(manager.tasks), settings.run_lease_seconds)
                    renewed = time.monotonic()
                await queue.reap(conn)
                await queue.expire_queued(conn, settings.max_queue_wait_s)
                free = settings.run_concurrency - len(manager.tasks)
                rows = await queue.claim(conn, owner, settings.run_lease_seconds, free)
        except TRANSIENT_DB_ERRORS:
            # A short database outage: the runs in flight carry on, and the next pass renews
            # their leases, well within the lease time.
            log.warning("run queue unavailable; retrying", exc_info=True)
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=2.0)
            continue
        for row in rows:
            fields = {"run_id": str(row["id"]), "work": row["work"]}
            log.info("run claimed", extra={"fields": fields})
            manager.start(row["id"], execution(row, store, llm, search, settings))
        if not rows:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=settings.run_poll_seconds)

    # Runs still executing are closed as incomplete, as at any shutdown.
    await manager.shutdown()
    await beat
    await redis.aclose()
    await pool.close()
    log.info("run worker stopped", extra={"fields": {"owner": owner}})


if __name__ == "__main__":
    asyncio.run(run())
