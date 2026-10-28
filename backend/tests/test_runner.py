"""The run queue and the run worker against a real PostgreSQL: claims, leases, and failures."""

import asyncio
import uuid

import psycopg
import pytest

from app.config import get_settings
from app.db import migrate, open_pool
from app.runner import execution
from app.runs import queue
from app.runs.manager import RunManager
from app.runs.store import RunStore
from tests.conftest import TEST_DATABASE_URL, needs_db, reset_schema

pytestmark = needs_db


@pytest.fixture
async def pool():
    reset_schema()
    await migrate(TEST_DATABASE_URL)
    p = await open_pool(TEST_DATABASE_URL, max_size=4)
    yield p
    await p.close()


async def new_session(pool) -> uuid.UUID:
    session_id = uuid.uuid4()
    async with pool.connection() as conn:
        await conn.execute(
            "INSERT INTO sessions (id, owner_hash) VALUES (%s, 'test')", (session_id,)
        )
    return session_id


async def queue_start(pool, session_id, question="q", faults=None) -> uuid.UUID:
    run_id = uuid.uuid4()
    async with pool.connection() as conn:
        await queue.enqueue_start(
            conn,
            run_id,
            session_id,
            "agent",
            question,
            None,
            faults or {},
            {"event": {"question": question}, "history": []},
        )
    return run_id


async def status(pool, run_id) -> tuple:
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT status, work, lease_owner, status_reason FROM runs WHERE id = %s", (run_id,)
        )
        return await cur.fetchone()


async def test_each_queued_run_is_claimed_once_oldest_first(pool):
    first = await queue_start(pool, await new_session(pool))
    second = await queue_start(pool, await new_session(pool))
    async with pool.connection() as conn:
        a = await queue.claim(conn, "worker-a", 60, 1)
        b = await queue.claim(conn, "worker-b", 60, 5)
        c = await queue.claim(conn, "worker-c", 60, 5)
    assert [r["id"] for r in a] == [first] and a[0]["work"] == "start"
    assert [r["id"] for r in b] == [second]
    assert c == []
    assert (await status(pool, first))[1:3] == (None, "worker-a")


async def test_a_run_whose_lease_ran_out_is_closed_not_rerun(pool):
    run_id = await queue_start(pool, await new_session(pool))
    async with pool.connection() as conn:
        await queue.claim(conn, "gone", 60, 1)
        assert await queue.reap(conn) == 0  # the lease is live
        await conn.execute("UPDATE runs SET lease_until = now() - interval '1 second'")
        assert await queue.reap(conn) == 1
        assert await queue.claim(conn, "other", 60, 5) == []  # never claimed again
    state, work, owner, reason = await status(pool, run_id)
    assert (state, work, owner) == ("incomplete", None, None)
    assert "stopped" in reason


async def test_renewing_keeps_a_lease_alive(pool):
    run_id = await queue_start(pool, await new_session(pool))
    async with pool.connection() as conn:
        await queue.claim(conn, "w", 1, 1)
        await asyncio.sleep(1.1)
        await queue.renew(conn, "w", [run_id], 60)
        assert await queue.reap(conn) == 0
        await queue.renew(conn, "someone-else", [run_id], 0)  # only the owner renews
        assert await queue.reap(conn) == 0


async def test_a_failed_first_event_closes_the_run_and_frees_the_session(pool):
    session_id = await new_session(pool)
    run_id = await queue_start(pool, session_id)

    class FailingStore(RunStore):
        async def event(self, run_id, type_, data):
            if type_ == "run_started":
                raise psycopg.OperationalError("connection lost")
            return await super().event(run_id, type_, data)

    store = FailingStore(pool)
    manager = RunManager(store)
    async with pool.connection() as conn:
        (row,) = await queue.claim(conn, "w", 60, 1)
    manager.start(run_id, execution(row, store, None, None, get_settings()))
    await asyncio.gather(*manager.tasks.values())

    assert (await status(pool, run_id))[0] == "failed"
    await queue_start(pool, session_id, "next question")  # the session takes a new question


async def test_a_resumed_run_keeps_its_faults(pool):
    await queue_start(pool, await new_session(pool), faults={"search_documents": "error"})
    async with pool.connection() as conn:
        await conn.execute(
            'UPDATE runs SET work = \'resume\', work_data = \'{"event": {"reply": "M-25-21"}}\''
        )
        (row,) = await queue.claim(conn, "w", 60, 1)
    assert row["work"] == "resume"
    assert row["faults"] == {"search_documents": "error"}
    assert row["work_data"]["event"] == {"reply": "M-25-21"}


async def test_a_run_that_cannot_even_start_fails_alone(pool):
    session_id = await new_session(pool)
    broken = await queue_start(pool, session_id)
    store = RunStore(pool)
    manager = RunManager(store)
    async with pool.connection() as conn:
        (row,) = await queue.claim(conn, "w", 60, 1)
    del row["faults"]  # a row the worker cannot set up
    manager.start(broken, execution(row, store, None, None, get_settings()))
    await asyncio.gather(*manager.tasks.values())
    assert (await status(pool, broken))[0] == "failed"
