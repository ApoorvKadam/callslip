"""What a running question needs, and the steps every run shares: events, history, finishing."""

import logging
import time
from dataclasses import dataclass, field
from uuid import UUID

from app.agent.evidence import build_answer, cited_pages, collect_evidence
from app.config import Settings
from app.llm import LLM, Usage
from app.retrieval.search import SearchHit, SearchService
from app.runs.store import RunStore

EXCERPT_CHARS = 180

log = logging.getLogger(__name__)


@dataclass
class RunContext:
    run_id: UUID
    session_id: UUID
    store: RunStore
    llm: LLM
    search: SearchService
    settings: Settings
    started: float = field(default_factory=time.monotonic)
    model_turns: int = 0
    tool_calls: int = 0

    def elapsed_s(self) -> float:
        return time.monotonic() - self.started

    def remaining_s(self) -> float:
        return self.settings.run_deadline_s - self.elapsed_s()

    async def emit(self, type_: str, data: dict) -> None:
        await self.store.event(self.run_id, type_, data)

    def answer_stream(self) -> "AnswerStream":
        """For the next model call: its text as it is written, for the browser to show."""
        return AnswerStream(self, self.model_turns + 1)

    async def model_event(self, purpose: str, stop_reason: str | None, usage: Usage) -> None:
        self.model_turns += 1
        await self.emit(
            "model_call",
            {
                "turn": self.model_turns,
                "model": getattr(self.llm, "model", None),
                "purpose": purpose,
                "stop_reason": stop_reason,
                "ms": usage.ms,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cache_read_tokens": usage.cache_read_tokens,
                "cache_creation_tokens": usage.cache_creation_tokens,
                "cost_usd": usage.cost_usd,
            },
        )

    async def finish(
        self, status: str, reason: str | None, final_content: list[dict] | None
    ) -> None:
        """Check citations in the final answer, store it, and close the run."""
        answer = None
        if final_content:
            messages = await self.store.messages(self.run_id)
            page_texts = await self.store.page_texts(cited_pages(final_content))
            answer = build_answer(final_content, collect_evidence(messages), page_texts)
        exec_ms = int(self.elapsed_s() * 1000)
        # Events first, status last: the event stream ends once the status is terminal, so
        # every event must already be stored by then.
        if answer is not None:
            await self.emit("answer", answer)
        totals = await self.store.usage_totals(self.run_id)
        await self.emit(
            "run_finished",
            {
                "status": status,
                "reason": reason,
                "model_turns": self.model_turns,
                "tool_calls": self.tool_calls,
                "ms": exec_ms,
                **totals,
            },
        )
        await self.store.update(
            self.run_id,
            status=status,
            status_reason=reason,
            answer=answer,
            model_turns=self.model_turns,
            tool_calls=self.tool_calls,
            exec_ms=exec_ms,
        )


def evidence_summary(hits: list[SearchHit]) -> list[dict]:
    """What the trace shows for retrieved passages: where each came from and how it starts."""
    return [
        {
            "document_id": h.document_id,
            "title": h.title,
            "page_no": h.page_no,
            "excerpt": h.text[:EXCERPT_CHARS],
            "score": round(h.score, 4),
        }
        for h in hits
    ]


class AnswerStream:
    """A model call's text as it arrives, sent as `answer_delta` events about four times a
    second. They only show progress: the answer itself is still built from the finished message,
    and its citations are checked as before. A failed write stops the progress events, not the run.
    """

    INTERVAL_S = 0.25

    def __init__(self, ctx: RunContext, turn: int) -> None:
        self.ctx, self.turn = ctx, turn
        self.pending, self.sent_at, self.broken = "", time.monotonic(), False

    async def add(self, text: str) -> None:
        self.pending += text
        if time.monotonic() - self.sent_at >= self.INTERVAL_S:
            await self.flush()

    async def flush(self) -> None:
        if not self.pending or self.broken:
            return
        try:
            await self.ctx.emit("answer_delta", {"turn": self.turn, "text": self.pending})
        except Exception:
            self.broken = True
            fields = {"run_id": str(self.ctx.run_id)}
            log.warning("answer progress stopped", extra={"fields": fields})
        self.pending, self.sent_at = "", time.monotonic()


def content_dicts(blocks: list) -> list[dict]:
    """SDK content blocks as plain JSON, unchanged, so they can be stored and sent back."""
    return [b.model_dump(mode="json", exclude_none=True) for b in blocks]


def question_text(question: str, history: list[tuple[str, str]]) -> str:
    """The user's question, preceded by earlier questions and answers of this session (plain
    text, no citations: citation-bearing text may not be sent back inside a user message)."""
    if not history:
        return question
    earlier = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in history)
    return f"Earlier in this conversation:\n{earlier}\n\nCurrent question: {question}"
