"""The agent: a plain tool-use loop with explicit limits.

Each turn the model sees the whole conversation and chooses one action: call a read tool, ask
the user a clarifying question, or answer. One tool call per turn (`disable_parallel_tool_use`)
keeps the order of events simple and means a clarification is never mixed with other calls.

Run states: running -> needs_clarification -> running -> complete | incomplete | failed.

Limits, all configurable: model turns, tool calls, a per-tool timeout with one retry, and a
wall-clock deadline with a reserve for the final answer. When a limit is reached, the last tool
result says so (a tool requested past a limit is answered "not run"), and one last call with
tool_choice "none" asks for the best answer from the evidence so far, marked incomplete. With
no time left for even that, the run stops with a deterministic summary of what it found,
without another model call.

Every message is stored append-only before the next call, so a paused run (and its citations)
can be rebuilt from the database exactly as the model saw it.
"""

import asyncio
import json
import logging
import time

import anthropic
import psycopg
import psycopg_pool
from pydantic import ValidationError

from app.agent.evidence import collect_evidence, parse_source
from app.agent.prompts import AGENT_SYSTEM
from app.agent.tools import (
    ARG_MODELS,
    TOOL_DEFINITIONS,
    ClarificationArgs,
    ToolOutcome,
    Tools,
    elapsed_ms,
    invalid_input,
)
from app.runs.context import RunContext, content_dicts, question_text

log = logging.getLogger(__name__)

AUTO = {"type": "auto", "disable_parallel_tool_use": True}
FINAL = {"type": "none"}
MIN_MODEL_CALL_S = 5.0
TRANSIENT_MODEL_ERRORS = (
    anthropic.APIConnectionError,  # includes the SDK's own timeouts
    TimeoutError,  # the call's total time budget (llm.py) ran out
    anthropic.RateLimitError,
    anthropic.InternalServerError,
)


# Real failures worth one retry: the dependency may answer the second time. Anything else (a
# bug) would fail the same way again, so it goes back to the model at once.
TRANSIENT_TOOL_ERRORS = (psycopg.OperationalError, psycopg_pool.PoolTimeout, OSError)


class ToolFailure(Exception):
    """A transient tool failure: retried once."""


def _system() -> list[dict]:
    # Tools and this system prompt never change between calls: they are the cached prefix.
    return [{"type": "text", "text": AGENT_SYSTEM, "cache_control": {"type": "ephemeral"}}]


def _tool_result(tool_use_id: str, outcome: ToolOutcome) -> dict:
    block = {"type": "tool_result", "tool_use_id": tool_use_id, "content": outcome.content}
    if outcome.is_error:
        block["is_error"] = True
    return block


def _not_run(reason: str) -> ToolOutcome:
    payload = {"status": "not_run", "reason": reason}
    return ToolOutcome(json.dumps(payload), True, "not_run", f"not run: {reason}")


def limit_before_tool(ctx: RunContext) -> str | None:
    if ctx.tool_calls >= ctx.settings.max_tool_calls:
        return f"the limit of {ctx.settings.max_tool_calls} tool calls was reached"
    if ctx.remaining_s() <= ctx.settings.finalize_reserve_s:
        return f"the time limit of {ctx.settings.run_deadline_s:g} seconds was nearly reached"
    return None


def limit_after_tool(ctx: RunContext) -> str | None:
    """Whether the next model turn has to be the final one."""
    if ctx.model_turns >= ctx.settings.max_model_turns - 1:
        return f"the limit of {ctx.settings.max_model_turns} model turns was reached"
    return limit_before_tool(ctx)


async def execute_tool(
    ctx: RunContext, tools: Tools, name: str, raw: dict, faults: dict[str, str]
) -> tuple[ToolOutcome, int, list[str]]:
    """Validate and run one read tool with a timeout and one retry. Returns the outcome, the
    number of attempts and the reasons for any retry."""
    model = ARG_MODELS.get(name)
    if model is None:
        return invalid_input(name, ValueError(f"unknown tool {name!r}")), 0, []
    try:
        args = model.model_validate(raw)
    except ValidationError as exc:
        return invalid_input(name, exc), 0, []

    handler = getattr(tools, name)
    retries: list[str] = []
    for attempt in (1, 2):
        timeout = max(1.0, min(ctx.settings.tool_timeout_s, ctx.remaining_s()))
        try:
            outcome = await asyncio.wait_for(
                _call(handler, args, name, attempt, faults, ctx.settings.tool_timeout_s), timeout
            )
            return outcome, attempt, retries
        except TimeoutError:
            reason, status, retryable = f"timed out after {timeout:g} s", "timeout", True
        except ToolFailure as exc:
            reason, status, retryable = str(exc), "error", True
        except Exception as exc:  # a real failure reaches the model as a typed error too
            fields = {"run_id": str(ctx.run_id), "tool": name}
            log.exception("tool failed", extra={"fields": fields})
            reason = f"failed unexpectedly ({type(exc).__name__})"
            status, retryable = "error", isinstance(exc, TRANSIENT_TOOL_ERRORS)
        retries.append(reason)
        if attempt == 2 or not retryable or ctx.remaining_s() <= ctx.settings.finalize_reserve_s:
            break
    payload = {"status": status, "tool": name, "error": reason, "attempts": len(retries)}
    return (
        ToolOutcome(json.dumps(payload), True, status, f"failed: {reason}"),
        len(retries),
        retries,
    )


async def _call(handler, args, name: str, attempt: int, faults: dict[str, str], timeout: float):
    """Run the handler; evaluation can inject a failure here (below the cache)."""
    mode = faults.get(name)
    if mode == "timeout" or (mode == "timeout_once" and attempt == 1):
        await asyncio.sleep(timeout + 5)  # the real timeout path cancels this
    if mode == "error" or (mode == "error_once" and attempt == 1):
        raise ToolFailure("the search backend is unavailable (injected fault)")
    return await handler(args)


async def start_agent(
    ctx: RunContext, question: str, history: list[tuple[str, str]], faults: dict[str, str]
) -> None:
    first = [{"type": "text", "text": question_text(question, history)}]
    await ctx.store.append_message(ctx.run_id, "user", first)
    await agent_loop(ctx, Tools(ctx.search, ctx.store, ctx.viewer), faults)


async def resume_agent(ctx: RunContext) -> None:
    await agent_loop(ctx, Tools(ctx.search, ctx.store, ctx.viewer), {})


async def agent_loop(ctx: RunContext, tools: Tools, faults: dict[str, str]) -> None:
    messages = await ctx.store.messages(ctx.run_id)
    note: str | None = None
    step = ctx.tool_calls
    while True:
        # The budget gate before every model call, including the first after a resume: the last
        # turn is kept for the final answer, and a spent budget stops without another call.
        if note is None and ctx.model_turns >= ctx.settings.max_model_turns - 1:
            note = f"the limit of {ctx.settings.max_model_turns} model turns was reached"
            await ctx.emit("limit", {"reason": note})
        final = note is not None
        if ctx.model_turns >= ctx.settings.max_model_turns or ctx.remaining_s() < MIN_MODEL_CALL_S:
            await stop_without_model(ctx, messages, note or "the time limit was reached")
            return
        timeout = (
            ctx.remaining_s() if final else ctx.remaining_s() - ctx.settings.finalize_reserve_s
        )
        progress = ctx.answer_stream()
        try:
            message, usage = await ctx.llm.create(
                run_id=ctx.run_id,
                purpose="agent_final" if final else "agent_turn",
                system=_system(),
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice=FINAL if final else AUTO,
                timeout_s=max(MIN_MODEL_CALL_S, min(ctx.settings.llm_timeout_s, timeout)),
                on_text=progress.add,
            )
            await progress.flush()
        except TRANSIENT_MODEL_ERRORS as exc:
            await stop_without_model(
                ctx, messages, f"the model could not be reached ({type(exc).__name__})"
            )
            return

        assistant = content_dicts(message.content)
        await ctx.store.append_message(ctx.run_id, "assistant", assistant)
        messages.append({"role": "assistant", "content": assistant})
        await ctx.model_event("final answer" if final else "decide", message.stop_reason, usage)

        if message.stop_reason == "refusal":
            await ctx.finish("failed", "the model declined to answer", None)
            return
        if message.stop_reason == "max_tokens":
            await ctx.finish("incomplete", "the answer hit the output length limit", assistant)
            return
        tool_use = next((b for b in message.content if b.type == "tool_use"), None)
        if final or tool_use is None:
            await ctx.finish("incomplete" if final else "complete", note, assistant)
            return

        if tool_use.name == "ask_clarification":
            # A question is only asked if a turn is left to use the reply; resume restores the
            # counts, so clarifications cannot run past the limits either.
            note = limit_after_tool(ctx)
            try:
                args = ClarificationArgs.model_validate(tool_use.input)
            except ValidationError as exc:
                outcome = invalid_input("ask_clarification", exc)
            else:
                if not note:
                    await pause_for_clarification(ctx, tool_use.id, args)
                    return
                outcome = _not_run(note)
        else:
            step += 1
            started = time.monotonic()
            note = limit_before_tool(ctx)
            attempts, retries = 0, []
            if note:
                outcome = _not_run(note)
            else:
                outcome, attempts, retries = await execute_tool(
                    ctx, tools, tool_use.name, tool_use.input, faults
                )
                ctx.tool_calls += 1
                note = limit_after_tool(ctx)
            await ctx.emit(
                "tool_call",
                {
                    "step": step,
                    "tool": tool_use.name,
                    "input": tool_use.input,
                    "status": outcome.status,
                    "summary": outcome.summary,
                    "ms": elapsed_ms(started),
                    "attempts": attempts,
                    "retries": retries,
                    **outcome.trace,
                },
            )

        content = [_tool_result(tool_use.id, outcome)]
        if note:
            await ctx.emit("limit", {"reason": note})
            content.append(
                {
                    "type": "text",
                    "text": f"Limit reached: {note}. Do not call more tools. Answer now using "
                    "only the evidence above, and say clearly what is incomplete.",
                }
            )
        await ctx.store.append_message(ctx.run_id, "user", content)
        messages.append({"role": "user", "content": content})


async def pause_for_clarification(ctx: RunContext, tool_use_id: str, args: ClarificationArgs):
    # Event first, status last: the event stream stops once the run is no longer running.
    await ctx.emit(
        "clarification",
        {"question": args.question, "options": args.options or [], "tool_use_id": tool_use_id},
    )
    await ctx.store.update(
        ctx.run_id,
        status="needs_clarification",
        pending_tool_use_id=tool_use_id,
        model_turns=ctx.model_turns,
        tool_calls=ctx.tool_calls,
        exec_ms=int(ctx.elapsed_s() * 1000),
    )


async def stop_without_model(ctx: RunContext, messages: list[dict], reason: str) -> None:
    """Stop with what was found so far, without another model call."""
    seen: list[str] = []
    for item in collect_evidence(messages):
        if parse_source(item.source) and item.title not in seen:
            seen.append(item.title)
    found = "\n".join(f"- {title}" for title in seen[:10]) or "- nothing yet"
    text = (
        f"I stopped before finishing because {reason}. I could not write a checked answer in "
        f"time. Passages found so far:\n{found}"
    )
    await ctx.finish("incomplete", reason, [{"type": "text", "text": text}])
