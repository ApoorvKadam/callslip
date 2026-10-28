"""A run worker's executing runs, as asyncio tasks (see app/runner.py).

A run that raises is marked `failed` with the reason; a run cancelled at shutdown is marked
`incomplete`. A run whose worker died without either is closed by the lease check in
runs/queue.py.
"""

import asyncio
import logging
import uuid
from collections.abc import Coroutine
from uuid import UUID

import anthropic

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
            await self._close(run_id, "incomplete", "stopped: the run worker shut down")
            raise
        except Exception as exc:  # the run fails; the server keeps going
            ref = uuid.uuid4().hex[:8]
            log.exception("run failed", extra={"fields": {"run_id": str(run_id), "ref": ref}})
            await self._close(run_id, "failed", public_reason(exc, ref))
        finally:
            self.tasks.pop(run_id, None)

    async def _close(self, run_id: UUID, status: str, reason: str) -> None:
        # Event first, status last (see RunContext.finish).
        await self.store.event(run_id, "run_finished", {"status": status, "reason": reason})
        await self.store.update(run_id, status=status, status_reason=reason)

    async def shutdown(self) -> None:
        for task in list(self.tasks.values()):
            task.cancel()
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)


def public_reason(exc: Exception, ref: str) -> str:
    """What users see when a run fails: a plain cause for known model API errors, otherwise a
    reference to the server log. Exception text can hold internal details, so it stays there."""
    if isinstance(exc, anthropic.AuthenticationError):
        cause = "the model API key was rejected"
    elif isinstance(exc, anthropic.RateLimitError):
        cause = "the model API is rate-limiting requests; try again shortly"
    elif isinstance(exc, anthropic.APIConnectionError):  # includes timeouts
        cause = "the model API could not be reached in time"
    elif isinstance(exc, anthropic.APIStatusError):
        cause = f"the model API returned an error ({exc.status_code})"
    else:
        cause = "an internal error occurred"
    return f"The run failed: {cause}. Reference {ref} in the server log."
