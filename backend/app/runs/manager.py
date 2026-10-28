"""Runs execute as background tasks in the API process; this keeps track of them.

A run that raises is marked `failed` with the reason; a run cancelled at shutdown is marked
`incomplete`. On startup, runs still marked `running` were interrupted by a restart and are
closed as `incomplete` (this assumes one API instance; see the scaling notes in the docs).
"""

import asyncio
import logging
from collections.abc import Coroutine
from uuid import UUID

from psycopg_pool import AsyncConnectionPool

from app.runs.store import RunStore

log = logging.getLogger(__name__)


class RunManager:
    def __init__(self, store: RunStore) -> None:
        self.store = store
        self.tasks: dict[UUID, asyncio.Task] = {}

    def start(self, run_id: UUID, work: Coroutine) -> None:
        self.tasks[run_id] = asyncio.create_task(self._guard(run_id, work))

    async def _guard(self, run_id: UUID, work: Coroutine) -> None:
        try:
            await work
        except asyncio.CancelledError:
            await self._close(run_id, "incomplete", "stopped: the server shut down")
            raise
        except Exception as exc:  # the run fails; the server keeps going
            log.exception("run failed", extra={"fields": {"run_id": str(run_id)}})
            await self._close(run_id, "failed", f"{type(exc).__name__}: {exc}"[:500])
        finally:
            self.tasks.pop(run_id, None)

    async def _close(self, run_id: UUID, status: str, reason: str) -> None:
        await self.store.update(run_id, status=status, status_reason=reason)
        await self.store.event(run_id, "run_finished", {"status": status, "reason": reason})

    async def shutdown(self) -> None:
        for task in list(self.tasks.values()):
            task.cancel()
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)


async def close_interrupted_runs(pool: AsyncConnectionPool) -> int:
    async with pool.connection() as conn:
        cur = await conn.execute(
            "UPDATE runs SET status = 'incomplete',"
            " status_reason = 'interrupted: the server restarted while it ran',"
            " updated_at = now(), finished_at = now() WHERE status = 'running'"
        )
        return cur.rowcount
