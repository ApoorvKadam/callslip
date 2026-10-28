"""The single-pass baseline: retrieve once with the question, generate once.

Same retriever, top_k, model, settings, citation format and answer rules as the agent, so the
evaluation compares only the difference that matters: the agent decides what to do next.
"""

from app.agent.evidence import search_result_block
from app.agent.prompts import BASELINE_SYSTEM
from app.retrieval.search import SearchFilters
from app.runs.context import RunContext, content_dicts, evidence_summary, question_text


async def run_baseline(ctx: RunContext, question: str, history: list[tuple[str, str]]) -> None:
    k = ctx.settings.top_k
    result = await ctx.search.search(question, SearchFilters(), k)
    ctx.tool_calls += 1
    await ctx.emit(
        "tool_call",
        {
            "step": 1,
            "tool": "search_documents",
            "input": {"query": question, "top_k": k},
            "status": "ok" if result.hits else "no_results",
            "summary": f"{len(result.hits)} passages",
            "cache": result.cache,
            "ms": result.ms,
            "evidence": evidence_summary(result.hits),
        },
    )

    text = question_text(question, history)
    if not result.hits:
        text = f"No passages were retrieved for this question.\n\n{text}"
    content = [
        *(search_result_block(h.document_id, h.title, h.page_no, h.text) for h in result.hits),
        {"type": "text", "text": text},
    ]
    await ctx.store.append_message(ctx.run_id, "user", content)

    message, usage = await ctx.llm.create(
        run_id=ctx.run_id,
        purpose="baseline_answer",
        system=[{"type": "text", "text": BASELINE_SYSTEM}],
        messages=[{"role": "user", "content": content}],
        timeout_s=max(5.0, min(ctx.settings.llm_timeout_s, ctx.remaining_s())),
    )
    assistant = content_dicts(message.content)
    await ctx.store.append_message(ctx.run_id, "assistant", assistant)
    await ctx.model_event("answer", message.stop_reason, usage)

    if message.stop_reason == "refusal":
        await ctx.finish("failed", "the model declined to answer", None)
    elif message.stop_reason == "max_tokens":
        await ctx.finish("incomplete", "the answer hit the output length limit", assistant)
    else:
        await ctx.finish("complete", None, assistant)
