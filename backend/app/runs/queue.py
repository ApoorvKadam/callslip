"""The run queue in PostgreSQL: claim queued runs, keep their leases, close abandoned ones.

`runs.work` says what a run is waiting for (start, or resume after a clarification). A worker
claims it by clearing `work` and taking a lease in one statement, with FOR UPDATE SKIP LOCKED,
so two workers never take the same run. The worker renews its leases while runs execute. A run
still marked running whose lease has run out lost its worker; it is closed, not re-run, because
part of it may already have executed (tool calls, model calls, events).
"""

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


async def enqueue_start(
    conn: AsyncConnection,
    run_id,
    session_id,
    mode,
    question,
    user_id,
    faults,
    work_data,
    compare_id=None,
) -> dict:
    cur = conn.cursor(row_factory=dict_row)
    await cur.execute(
        "INSERT INTO runs (id, session_id, mode, question, user_id, faults, work, work_data,"
        " compare_id) VALUES (%s, %s, %s, %s, %s, %s, 'start', %s, %s) RETURNING *",
        (run_id, session_id, mode, question, user_id, Jsonb(faults), Jsonb(work_data), compare_id),
    )
    return await cur.fetchone()


async def claim(conn: AsyncConnection, owner: str, lease_s: int, limit: int) -> list[dict]:
    """Take up to `limit` queued runs, oldest first, each with a lease of `lease_s` seconds."""
    if limit <= 0:
        return []
    cur = conn.cursor(row_factory=dict_row)
    await cur.execute(
        "WITH picked AS ("
        "    SELECT id, work FROM runs WHERE work IS NOT NULL AND status = 'running'"
        "    ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT %(limit)s)"
        " UPDATE runs r SET work = NULL, lease_owner = %(owner)s,"
        "        lease_until = now() + %(lease)s * interval '1 second', updated_at = now()"
        "   FROM picked p WHERE r.id = p.id"
        " RETURNING r.id, r.session_id, r.mode, r.question, p.work, r.work_data, r.faults,"
        "           r.user_id, r.exec_ms, r.model_turns, r.tool_calls",
        {"owner": owner, "lease": lease_s, "limit": limit},
    )
    return await cur.fetchall()


async def renew(conn: AsyncConnection, owner: str, run_ids: list, lease_s: int) -> None:
    if run_ids:
        await conn.execute(
            "UPDATE runs SET lease_until = now() + %s * interval '1 second'"
            " WHERE id = ANY(%s) AND lease_owner = %s AND status = 'running'",
            (lease_s, run_ids, owner),
        )


async def expire_queued(conn: AsyncConnection, max_wait_s: float) -> int:
    """Close runs that waited in the queue longer than `max_wait_s`: with no worker free, the
    user gets an answer that says so, and the question is never run long after they left."""
    cur = await conn.execute(
        "UPDATE runs SET status = 'incomplete', work = NULL,"
        " status_reason = 'no run worker started this question in time; ask it again',"
        " updated_at = now(), finished_at = now()"
        " WHERE status = 'running' AND work IS NOT NULL"
        " AND updated_at < now() - %s * interval '1 second'",
        (max_wait_s,),
    )
    return cur.rowcount


async def reap(conn: AsyncConnection) -> int:
    """Close runs whose worker is gone: running, not queued, and with no live lease."""
    cur = await conn.execute(
        "UPDATE runs SET status = 'incomplete',"
        " status_reason = 'interrupted: the run worker stopped while it ran',"
        " lease_owner = NULL, updated_at = now(), finished_at = now()"
        " WHERE status = 'running' AND work IS NULL"
        " AND coalesce(lease_until, '-infinity') < now()"
    )
    return cur.rowcount
