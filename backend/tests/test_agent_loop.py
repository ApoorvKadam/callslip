"""The agent loop's control flow, replaying real recorded model turns (no live model calls).

tests/fixtures/agent_runs.json holds the turns of two real runs: one that asked a clarifying
question, and one whose searches failed so it read pages instead. A replay client hands those
turns back in order (or the recorded final answer when the loop forces one), so the loop's
own deterministic logic runs for real: tools against PostgreSQL, limits, pause and resume,
message storage and events.
"""

import json
import uuid
from pathlib import Path

import pytest
from anthropic.types import Message

from app.agent.loop import FINAL, resume_agent, start_agent
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

    async def create(self, *, tool_choice=None, **_):
        self.tool_choices.append(tool_choice)
        turn = self.final if tool_choice == FINAL else self.turns.pop(0)
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
    assert llm.tool_choices[:-1] == [{"type": "auto", "disable_parallel_tool_use": True}] * 2
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
    await resume_agent(ctx)

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
