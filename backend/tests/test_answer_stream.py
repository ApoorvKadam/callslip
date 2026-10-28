"""Answer progress: batched, and never able to fail a run."""

import asyncio
import uuid

from app.runs.context import AnswerStream


class Ctx:
    def __init__(self, fail: bool = False) -> None:
        self.run_id, self.fail, self.sent = uuid.uuid4(), fail, []

    async def emit(self, type_: str, data: dict) -> None:
        if self.fail:
            raise OSError("database unavailable")
        self.sent.append((type_, data))


def test_pieces_are_batched_and_flushed_in_order():
    ctx = Ctx()
    stream = AnswerStream(ctx, turn=3)

    async def run():
        for piece in ("The ", "memo ", "says"):
            await stream.add(piece)
        await stream.flush()

    asyncio.run(run())
    assert "".join(d["text"] for _, d in ctx.sent) == "The memo says"
    assert len(ctx.sent) == 1  # the pieces arrived within one interval
    assert ctx.sent[0] == ("answer_delta", {"turn": 3, "text": "The memo says"})


def test_a_failed_write_stops_progress_but_not_the_run():
    ctx = Ctx(fail=True)
    stream = AnswerStream(ctx, turn=1)

    async def run():
        await stream.add("text")
        await stream.flush()  # raises inside, swallowed
        ctx.fail = False
        await stream.add("more")
        await stream.flush()

    asyncio.run(run())
    assert stream.broken and ctx.sent == []
