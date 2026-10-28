"""The agent loop's control flow, replaying real recorded model turns (no live model calls).

tests/fixtures/agent_runs.json holds the turns of two real runs: one that asked a clarifying
question, and one whose searches failed so it read pages instead. A replay client hands those
turns back in order (or the recorded final answer when the loop forces one), so the loop's
own deterministic logic runs for real: tools against PostgreSQL, limits, pause and resume,
message storage and events.
"""

import asyncio
import json
import time
import uuid
from pathlib import Path

import psycopg
import pytest
from anthropic.types import Message

from app.agent.baseline import run_baseline
from app.agent.loop import AUTO, FINAL, catalog, resume_agent, start_agent
from app.agent.tools import ToolOutcome, Tools
from app.config import get_settings
from app.llm import Usage
from app.runs.context import RunContext
from tests.test_tools import embedder, tools  # noqa: F401 - shared fixtures

pytestmark = pytest.mark.usefixtures("tools")

RUNS = {
    r["question"]: r["turns"]
    for r in json.loads((Path(__file__).parent / "fixtures" / "agent_runs.json").read_text())[
        "runs"
    ]
}
AMBIGUOUS = next(q for q in RUNS if q.startswith("What does the memo"))
FAILED_SEARCH = next(q for q in RUNS if q.startswith("How does the NIST Generative AI"))


class ReplayLLM:
    """Returns recorded turns in order; returns the recorded final answer when forced to answer."""

    def __init__(self, turns: list[dict]) -> None:
        self.turns = list(turns)
        self.final = turns[-1]
        self.tool_choices: list[dict | None] = []
        self.cached: list[bool] = []

    async def create(
        self,
        *,
        tool_choice=None,
        on_text=None,
        purpose=None,
        messages=(),
        cache_conversation=False,
        **_,
    ):
        if purpose == "support_check":
            return self.judge(messages)
        self.tool_choices.append(tool_choice)
        self.cached.append(cache_conversation)
        turn = self.final if tool_choice == FINAL else self.turns.pop(0)
        if on_text:  # stream each text block in two pieces, as the real client would
            for block in turn["content"]:
                if block["type"] == "text":
                    half = len(block["text"]) // 2
                    await on_text(block["text"][:half])
                    await on_text(block["text"][half:])
        message = Message.model_validate(
            {
                "id": "msg_replay",
                "type": "message",
                "role": "assistant",
                "model": "claude-sonnet-5-5",
                "content": turn["content"],
                "stop_reason": turn["stop_reason"],
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
        )
        return message, Usage(10, 5, 0, 0, 0.0001, 1)

    def judge(self, messages):
        """Rules every claim supported, as a well-formed judge reply would."""
        self.judged = len(json.loads(messages[0]["content"]))
        checks = [
            {"claim": i, "verdict": "supported", "reason": "stated"}
            for i in range(1, self.judged + 1)
        ]
        message = Message.model_validate(
            {
                "id": "msg_judge",
                "type": "message",
                "role": "assistant",
                "model": "claude-haiku-5-5",
                "content": [{"type": "text", "text": json.dumps({"checks": checks})}],
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
        )
        return message, Usage(10, 5, 0, 0, 0.0001, 1)


async def new_run(tools, llm, **limits) -> RunContext:  # noqa: F811 - pytest fixture param
    store = tools.store
    session_id, run_id = uuid.uuid4(), uuid.uuid4()
    async with store.pool.connection() as conn:
        await conn.execute(
            "INSERT INTO sessions (id, owner_hash) VALUES (%s, 'test')", (session_id,)
        )
        await conn.execute(
            "INSERT INTO runs (id, session_id, mode, question) VALUES (%s, %s, 'agent', 'q')",
            (run_id, session_id),
        )
    settings = get_settings().model_copy(update=limits)
    return RunContext(run_id, session_id, store, llm, tools.search, settings)


async def events(ctx: RunContext) -> list[tuple[str, dict]]:
    async with ctx.store.pool.connection() as conn:
        cur = await conn.execute(
            "SELECT type, data FROM run_events WHERE run_id = %s ORDER BY seq", (ctx.run_id,)
        )
        return await cur.fetchall()


async def test_tool_call_limit_forces_a_final_answer_marked_incomplete(tools):  # noqa: F811
    llm = ReplayLLM(RUNS[FAILED_SEARCH])
    ctx = await new_run(tools, llm, max_tool_calls=2)
    await start_agent(ctx, FAILED_SEARCH, [], {})

    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "incomplete"
    assert "2 tool calls" in run["status_reason"]
    assert run["tool_calls"] == 2
    # The last call was forced to answer: tool_choice "none".
    assert llm.tool_choices[-1] == FINAL
    assert llm.tool_choices[:-1] == [AUTO] * 2
    kinds = [t for t, _ in await events(ctx)]
    assert kinds.index("limit") < kinds.index("run_finished")
    # The note telling the model to stop is in the last stored user message.
    messages = await ctx.store.messages(ctx.run_id)
    assert messages[-2]["content"][-1]["text"].startswith("Limit reached:")


async def test_a_recorded_answer_cites_evidence_this_run_never_saw(tools):  # noqa: F811
    # Replayed citations point at passages from the original run, so none can be verified here:
    # the check is against what this run actually sent, not what the model claims.
    llm = ReplayLLM(RUNS[FAILED_SEARCH])
    ctx = await new_run(tools, llm, max_tool_calls=2)
    await start_agent(ctx, FAILED_SEARCH, [], {})
    answer = (await ctx.store.get_run(ctx.run_id))["answer"]
    assert answer["citations"]
    assert answer["citations_verified"] < len(answer["citations"])


async def test_clarification_pauses_then_resumes_the_same_run(tools):  # noqa: F811
    llm = ReplayLLM(RUNS[AMBIGUOUS])
    ctx = await new_run(tools, llm)
    await start_agent(ctx, AMBIGUOUS, [], {})

    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "needs_clarification"
    asked = [d for t, d in await events(ctx) if t == "clarification"][-1]
    assert run["pending_tool_use_id"] == asked["tool_use_id"]
    assert asked["options"]

    # What the resume endpoint does: append the reply as the tool's result, then continue.
    reply = {
        "type": "tool_result",
        "tool_use_id": asked["tool_use_id"],
        "content": "The user replied: OMB M-25-21",
    }
    await ctx.store.append_message(ctx.run_id, "user", [reply])
    await ctx.store.update(ctx.run_id, status="running", pending_tool_use_id=None)
    await resume_agent(ctx, {})

    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "complete"
    roles = [m["role"] for m in await ctx.store.messages(ctx.run_id)]
    assert roles == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
    ]


async def test_no_time_left_stops_without_another_model_call(tools):  # noqa: F811
    llm = ReplayLLM(RUNS[FAILED_SEARCH])
    ctx = await new_run(tools, llm, run_deadline_s=1.0)
    await start_agent(ctx, FAILED_SEARCH, [], {})
    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "incomplete"
    assert llm.tool_choices == []  # never called the model
    assert "stopped before finishing" in run["answer"]["text"]


async def test_a_clarification_needs_a_turn_left_to_use_the_reply(tools):  # noqa: F811
    llm = ReplayLLM(RUNS[AMBIGUOUS])  # recorded: list_documents, then ask_clarification
    ctx = await new_run(tools, llm, max_model_turns=3)
    await start_agent(ctx, AMBIGUOUS, [], {})
    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "incomplete"  # answered within the limit instead of pausing
    assert llm.tool_choices[-1] == FINAL
    assert "limit" in [t for t, _ in await events(ctx)]


class TimeoutLLM:
    """A model call whose total time budget runs out (the wait_for in llm.py)."""

    async def create(self, **_):
        raise TimeoutError


async def test_model_timeout_ends_incomplete_with_what_was_found(tools):  # noqa: F811
    ctx = await new_run(tools, TimeoutLLM())
    await start_agent(ctx, FAILED_SEARCH, [], {})
    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "incomplete"
    assert "TimeoutError" in run["status_reason"]
    assert "stopped before finishing" in run["answer"]["text"]


async def test_baseline_model_timeout_ends_incomplete(tools):  # noqa: F811
    ctx = await new_run(tools, TimeoutLLM())
    await run_baseline(ctx, FAILED_SEARCH, [])
    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "incomplete"
    assert "TimeoutError" in run["status_reason"]


@pytest.mark.parametrize(
    ("error", "attempts"),
    [
        (psycopg.OperationalError("the connection to the server was lost"), 2),  # may recover
        (RuntimeError("a bug"), 1),  # would fail the same way again
    ],
)
async def test_a_real_tool_exception_goes_back_as_a_typed_error(
    tools,  # noqa: F811
    monkeypatch,
    error,
    attempts,
):
    async def broken(self, args):
        raise error

    monkeypatch.setattr(Tools, "search_documents", broken)
    ctx = await new_run(tools, ReplayLLM(RUNS[FAILED_SEARCH]))
    await start_agent(ctx, FAILED_SEARCH, [], {})
    searches = [
        d for t, d in await events(ctx) if t == "tool_call" and d["tool"] == "search_documents"
    ]
    assert searches and all(d["status"] == "error" for d in searches)
    name = type(error).__name__
    assert all(d["attempts"] == attempts and name in d["summary"] for d in searches)
    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "complete"  # the model moved on to reading pages, as recorded


@pytest.mark.parametrize(("used", "calls"), [(2, 0), (1, 1)])
async def test_a_resumed_run_respects_the_turn_budget(tools, used, calls):  # noqa: F811
    llm = ReplayLLM(RUNS[FAILED_SEARCH])
    ctx = await new_run(tools, llm, max_model_turns=2)
    ctx.model_turns = used  # as restored from the database on resume
    await resume_agent(ctx, {})
    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "incomplete"
    assert llm.tool_choices == [FINAL] * calls  # only the final answer, or nothing at all


async def test_streamed_text_adds_up_to_the_final_answer(tools):  # noqa: F811
    llm = ReplayLLM(RUNS[FAILED_SEARCH])
    ctx = await new_run(tools, llm)
    await start_agent(ctx, FAILED_SEARCH, [], {})

    recorded = await events(ctx)
    final_turn = max(d["turn"] for t, d in recorded if t == "model_call")
    pieces = [d for t, d in recorded if t == "answer_delta" and d["turn"] == final_turn]
    streamed = "".join(d["text"] for d in pieces)
    answer = next(d for t, d in recorded if t == "answer")
    assert streamed and streamed == answer["text"]
    # Progress comes before the answer, which is still built from the finished message.
    kinds = [t for t, _ in recorded]
    assert max(i for i, k in enumerate(kinds) if k == "answer_delta") < kinds.index("answer")


async def test_each_cited_piece_of_the_answer_gets_a_support_verdict(tools):  # noqa: F811
    llm = ReplayLLM(RUNS[FAILED_SEARCH])
    ctx = await new_run(tools, llm)
    await start_agent(ctx, FAILED_SEARCH, [], {})

    recorded = await events(ctx)
    kinds = [t for t, _ in recorded]
    assert kinds.index("answer") < kinds.index("support") < kinds.index("run_finished")
    checks = next(d for t, d in recorded if t == "support")["checks"]
    assert len(checks) == llm.judged > 0
    assert {c["verdict"] for c in checks} == {"supported"}
    run = await ctx.store.get_run(ctx.run_id)
    assert run["answer"]["support"] == checks  # stored with the answer


async def test_a_failed_support_check_leaves_the_answer_and_marks_pieces_unchecked(
    tools,  # noqa: F811
):
    llm = ReplayLLM(RUNS[FAILED_SEARCH])

    def broken(messages):
        raise TimeoutError

    llm.judge = broken
    ctx = await new_run(tools, llm)
    await start_agent(ctx, FAILED_SEARCH, [], {})

    run = await ctx.store.get_run(ctx.run_id)
    assert run["status"] == "complete" and run["answer"]["text"]
    assert {c["verdict"] for c in run["answer"]["support"]} == {"not_checked"}


def tool_turn(*calls: tuple[str, dict]) -> dict:
    """A model turn that asks for these tool calls, in this order."""
    content = [
        {"type": "tool_use", "id": f"toolu_{n}", "name": name, "input": args}
        for n, (name, args) in enumerate(calls)
    ]
    return {"stop_reason": "tool_use", "content": content}


DONE = {"stop_reason": "end_turn", "content": [{"type": "text", "text": "That is all I found."}]}


async def test_one_turns_tool_calls_run_together_and_report_in_order(
    tools,  # noqa: F811
    monkeypatch,
):
    spans: dict[str, tuple[float, float]] = {}

    async def search(self, args):
        started = time.monotonic()
        if args.query == "boom":
            raise RuntimeError("a bug")
        await asyncio.sleep(0.3)
        spans[args.query] = (started, time.monotonic())
        return ToolOutcome(json.dumps({"status": "no_results"}), False, "no_results", "none")

    monkeypatch.setattr(Tools, "search_documents", search)
    turn = tool_turn(*[("search_documents", {"query": q}) for q in ("first", "second", "boom")])
    ctx = await new_run(tools, ReplayLLM([turn, DONE]))
    await start_agent(ctx, "q", [], {})

    # The second search started before the first one ended: they ran at the same time.
    assert spans["second"][0] < spans["first"][1]
    calls = [d for t, d in await events(ctx) if t == "tool_call"]
    assert [(c["step"], c["input"]["query"]) for c in calls] == [
        (1, "first"),
        (2, "second"),
        (3, "boom"),
    ]
    assert calls[0]["ms"] >= 300 and calls[1]["ms"] >= 300
    assert (calls[2]["status"], calls[2]["attempts"]) == ("error", 1)
    # One result per call, in the order asked, all in one message; the failure alone is an error.
    results = (await ctx.store.messages(ctx.run_id))[2]["content"]
    assert [r["tool_use_id"] for r in results] == ["toolu_0", "toolu_1", "toolu_2"]
    assert [r.get("is_error", False) for r in results] == [False, False, True]
    run = await ctx.store.get_run(ctx.run_id)
    assert (run["status"], run["tool_calls"]) == ("complete", 3)


async def test_a_clarification_asked_alongside_searches_is_not_run(tools):  # noqa: F811
    turn = tool_turn(
        ("ask_clarification", {"question": "Which memo?", "options": ["A", "B"]}),
        ("search_documents", {"query": "functions of the core"}),
    )
    ctx = await new_run(tools, ReplayLLM([turn, DONE]))
    await start_agent(ctx, "q", [], {})

    run = await ctx.store.get_run(ctx.run_id)
    assert (run["status"], run["tool_calls"]) == ("complete", 1)
    kinds = [t for t, _ in await events(ctx)]
    assert "clarification" not in kinds
    calls = [d for t, d in await events(ctx) if t == "tool_call"]
    assert calls[0]["tool"] == "ask_clarification" and calls[0]["status"] == "not_run"
    assert calls[1]["tool"] == "search_documents" and calls[1]["status"] != "not_run"
    results = (await ctx.store.messages(ctx.run_id))[2]["content"]
    assert "only call in its turn" in results[0]["content"]


async def test_calls_past_the_tool_budget_are_answered_not_run(tools):  # noqa: F811
    turn = tool_turn(*[("search_documents", {"query": q}) for q in ("one", "two", "three")])
    llm = ReplayLLM([turn, DONE])
    ctx = await new_run(tools, llm, max_tool_calls=1)
    await start_agent(ctx, "q", [], {})

    calls = [d for t, d in await events(ctx) if t == "tool_call"]
    assert [c["status"] == "not_run" for c in calls] == [False, True, True]
    content = (await ctx.store.messages(ctx.run_id))[2]["content"]
    assert [b["type"] for b in content] == ["tool_result"] * 3 + ["text"]
    assert content[-1]["text"].startswith("Limit reached:")
    run = await ctx.store.get_run(ctx.run_id)
    assert (run["status"], run["tool_calls"]) == ("incomplete", 1)
    # The forced final answer is not cached: a different tool_choice cannot reuse the cache.
    assert llm.tool_choices == [AUTO, FINAL]
    assert llm.cached == [True, False]


async def test_the_first_message_lists_what_this_user_can_search(tools):  # noqa: F811
    async with tools.store.pool.connection() as conn:
        cur = await conn.execute(
            "INSERT INTO users (email, password_hash) VALUES ('a@x.edu', 'x') RETURNING id"
        )
        other = (await cur.fetchone())[0]
        await conn.execute(
            "INSERT INTO documents (title, filename, sha256, byte_size, status, owner_user_id)"
            " VALUES ('Private notes', 'p.pdf', 'p', 1, 'ready', %s)",
            (other,),
        )
    ctx = await new_run(tools, ReplayLLM([DONE]))
    await start_agent(ctx, "What is in here?", [], {})

    first = (await ctx.store.messages(ctx.run_id))[0]["content"]
    listed = first[0]["text"]
    assert "NIST AI RMF" in listed and "OMB M-25-21" in listed
    assert "Draft" not in listed  # not ready yet
    assert "Private notes" not in listed  # someone else's
    assert first[1]["text"] == "What is in here?"
    run = await ctx.store.get_run(ctx.run_id)
    assert 0 < run["answer"]["answer_ms"] <= run["exec_ms"]


async def test_a_document_list_that_cannot_load_is_reported_not_empty(
    tools,  # noqa: F811
    monkeypatch,
):
    async def broken(self, args):
        raise psycopg.OperationalError("the connection to the server was lost")

    monkeypatch.setattr(Tools, "list_documents", broken)
    text = await catalog(tools)
    assert "could not be loaded" in text and "list_documents" in text
