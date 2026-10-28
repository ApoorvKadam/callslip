"""The single-pass baseline: retrieve once with the question, generate once.

Same retriever and search executor (timeout, one retry, fault injection), top_k, model,
settings, citation format and answer rules as the agent, so the evaluation compares only the
difference that matters: the agent decides what to do next, the baseline cannot.
"""

import time

from app.agent.loop import TRANSIENT_MODEL_ERRORS, execute_tool, stop_without_model
from app.agent.prompts import BASELINE_SYSTEM
from app.agent.tools import Tools, elapsed_ms
from app.runs.context import RunContext, content_dicts, question_text


async def run_baseline(
    ctx: RunContext,
    question: str,
    history: list[tuple[str, str]],
    faults: dict[str, str] | None = None,
) -> None:
    started = time.monotonic()
    # The search tool takes queries of up to 500 characters (the agent writes its own, shorter
    # ones). A longer question is searched by its first 500; the model still reads all of it.
    query = {"query": question[:500], "top_k": ctx.settings.top_k}
    outcome, attempts, retries = await execute_tool(
        ctx, Tools(ctx.search, ctx.store), "search_documents", query, faults or {}
    )
    ctx.tool_calls += 1
    await ctx.emit(
        "tool_call",
        {
            "step": 1,
            "tool": "search_documents",
            "input": query,
            "status": outcome.status,
            "summary": outcome.summary,
            "ms": elapsed_ms(started),
            "attempts": attempts,
            "retries": retries,
            **outcome.trace,
        },
    )

    passages = outcome.content if outcome.status == "ok" else []
    text = question_text(question, history)
    if not passages:
        why = (
            "No passages were retrieved for this question."
            if outcome.status == "no_results"
            else f"The search failed ({outcome.summary}), so no passages are available."
        )
        text = f"{why}\n\n{text}"
    content = [*passages, {"type": "text", "text": text}]
    await ctx.store.append_message(ctx.run_id, "user", content)

    messages = [{"role": "user", "content": content}]
    try:
        message, usage = await ctx.llm.create(
            run_id=ctx.run_id,
            purpose="baseline_answer",
            system=[{"type": "text", "text": BASELINE_SYSTEM}],
            messages=messages,
            timeout_s=max(5.0, min(ctx.settings.llm_timeout_s, ctx.remaining_s())),
        )
    except TRANSIENT_MODEL_ERRORS as exc:
        reason = f"the model could not be reached ({type(exc).__name__})"
        await stop_without_model(ctx, messages, reason)
        return
    assistant = content_dicts(message.content)
    await ctx.store.append_message(ctx.run_id, "assistant", assistant)
    await ctx.model_event("answer", message.stop_reason, usage)

    if message.stop_reason == "refusal":
        await ctx.finish("failed", "the model declined to answer", None)
    elif message.stop_reason == "max_tokens":
        await ctx.finish("incomplete", "the answer hit the output length limit", assistant)
    elif outcome.is_error:
        await ctx.finish("incomplete", f"retrieval failed: {outcome.summary}", assistant)
    else:
        await ctx.finish("complete", None, assistant)
