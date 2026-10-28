"""Read a run, and follow its steps live as server-sent events.

The event stream replays stored events (each with a stable SSE id, so a reconnect sends
`Last-Event-ID` and gets only what it missed), then follows new ones until the run ends or
pauses for a clarification. Reconnecting or refreshing never re-runs anything.
"""

import asyncio
import json
import time
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from psycopg.rows import dict_row

from app.api.sessions import RUN_COLUMNS, Owner, Pool

router = APIRouter(prefix="/api/runs", tags=["runs"])

POLL_S = 0.4
HEARTBEAT_S = 15.0


async def owned_run(pool, run_id: UUID, owner: str) -> dict:
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            f"SELECT {', '.join(f'r.{c}' for c in RUN_COLUMNS)}"
            " FROM runs r JOIN sessions s ON s.id = r.session_id"
            " WHERE r.id = %s AND s.owner_hash = %s",
            (run_id, owner),
        )
        run = await cur.fetchone()
    if run is None:
        raise HTTPException(404, "Not found.")
    return run


@router.get("/{run_id}")
async def get_run(run_id: UUID, pool: Pool, owner: Owner) -> dict:
    run = await owned_run(pool, run_id, owner)
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            "SELECT seq, type, data, created_at FROM run_events WHERE run_id = %s ORDER BY seq",
            (run_id,),
        )
        run["events"] = await cur.fetchall()
    return run


@router.get("/{run_id}/events")
async def run_events(run_id: UUID, request: Request, pool: Pool, owner: Owner):
    await owned_run(pool, run_id, owner)
    try:
        last_seen = int(request.headers.get("last-event-id", "0"))
    except ValueError:
        last_seen = 0

    async def stream():
        nonlocal last_seen
        last_beat = time.monotonic()
        while not await request.is_disconnected():
            async with pool.connection() as conn:
                cur = await conn.execute(
                    "SELECT seq, type, data FROM run_events WHERE run_id = %s AND seq > %s"
                    " ORDER BY seq",
                    (run_id, last_seen),
                )
                rows = await cur.fetchall()
                cur = await conn.execute("SELECT status FROM runs WHERE id = %s", (run_id,))
                status = (await cur.fetchone())[0]
            for seq, type_, data in rows:
                last_seen = seq
                yield f"id: {seq}\nevent: {type_}\ndata: {json.dumps(data, default=str)}\n\n"
            if status != "running" and not rows:
                yield f"event: end\ndata: {json.dumps({'status': status})}\n\n"
                return
            if time.monotonic() - last_beat > HEARTBEAT_S:
                last_beat = time.monotonic()
                yield ": keep-alive\n\n"
            await asyncio.sleep(POLL_S)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
