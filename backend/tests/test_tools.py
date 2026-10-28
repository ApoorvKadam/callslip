"""Tool contracts against a real PostgreSQL and the real embedding model.

Each read tool has four documented result shapes: success, empty (not an error), invalid input
(an error the model must fix) and failure. These tests pin each one.
"""

import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.agent.loop import execute_tool, limit_after_tool, limit_before_tool
from app.agent.tools import ClarificationArgs, SearchArgs, SectionArgs, Tools
from app.cache import Cache
from app.config import get_settings
from app.db import migrate, open_pool
from app.embeddings import Embedder
from app.retrieval.search import SearchService
from app.runs.store import RunStore
from tests.conftest import TEST_DATABASE_URL, make_pdf, needs_db, needs_model, reset_schema
from tests.test_ingest_and_search import MEMO_PAGE, RMF_PAGE

pytestmark = [needs_db, needs_model]


@pytest.fixture(scope="module")
def embedder():
    s = get_settings()
    return Embedder(s.embed_model, s.fastembed_cache_path, 2, s.embed_batch_size)


@pytest.fixture
async def tools(embedder):
    reset_schema()
    await migrate(TEST_DATABASE_URL)
    pool = await open_pool(TEST_DATABASE_URL, max_size=2)
    # Two ready documents and one still processing, ingested by the worker's own code.
    from app.ingest import jobs
    from app.worker import process

    async with pool.connection() as conn:
        for title, pages, sha in (
            ("NIST AI RMF", ["Cover.", RMF_PAGE], "a"),
            ("OMB M-25-21", [MEMO_PAGE], "b"),
            ("Draft", ["Not ready yet."], "c"),
        ):
            cur = await conn.execute(
                "INSERT INTO documents (title, filename, sha256, byte_size) VALUES (%s, %s, %s, 1)"
                " RETURNING id",
                (title, f"{sha}.pdf", sha),
            )
            doc_id = (await cur.fetchone())[0]
            await conn.execute(
                "INSERT INTO document_files (document_id, content) VALUES (%s, %s)",
                (doc_id, make_pdf(pages)),
            )
    settings = get_settings()
    for _ in range(2):  # the third stays queued
        async with pool.connection() as conn:
            job = await jobs.claim_next(conn, "test", 60, 3)
        await process(pool, embedder, settings, job, "test")
    from redis.asyncio import Redis

    cache = Cache(Redis.from_url("redis://127.0.0.1:1/0", socket_connect_timeout=0.1))
    yield Tools(SearchService(pool, embedder, cache), RunStore(pool))
    await pool.close()


def ctx(remaining: float = 60.0, tool_calls: int = 0, model_turns: int = 0):
    """The parts of a run context the tool executor and limit checks read."""
    settings = get_settings().model_copy(update={"tool_timeout_s": 1.0})
    return SimpleNamespace(
        settings=settings,
        remaining_s=lambda: remaining,
        tool_calls=tool_calls,
        model_turns=model_turns,
    )


async def test_list_documents_returns_only_ready_documents_as_json(tools):
    out = await tools.list_documents(None)
    assert (out.status, out.is_error) == ("ok", False)
    titles = [d["title"] for d in json.loads(out.content)["documents"]]
    assert titles == ["NIST AI RMF", "OMB M-25-21"]


async def test_search_success_is_citable_search_results(tools):
    out = await tools.search_documents(SearchArgs(query="four functions of the core"))
    assert out.status == "ok" and not out.is_error
    assert all(block["type"] == "search_result" for block in out.content)
    assert out.content[0]["citations"] == {"enabled": True}
    assert out.content[0]["source"] == "doc-1/p2"
    assert out.trace["evidence"][0]["page_no"] == 2


async def test_search_with_nothing_matching_is_an_empty_result_not_an_error(tools):
    out = await tools.search_documents(SearchArgs(query="anything", page_from=40))
    assert (out.status, out.is_error) == ("no_results", False)
    assert json.loads(out.content)["status"] == "no_results"


async def test_read_section_returns_one_result_per_page(tools):
    out = await tools.read_document_section(SectionArgs(document_id=1, page_start=1, page_end=2))
    assert out.status == "ok"
    assert [b["source"] for b in out.content] == ["doc-1/p1", "doc-1/p2"]


async def test_read_section_past_the_last_page_is_invalid_input(tools):
    out = await tools.read_document_section(SectionArgs(document_id=1, page_start=2, page_end=3))
    assert (out.status, out.is_error) == ("invalid_input", True)
    assert "has 2 pages" in json.loads(out.content)["error"]


async def test_read_section_of_a_document_that_is_not_ready_is_invalid_input(tools):
    out = await tools.read_document_section(SectionArgs(document_id=3, page_start=1, page_end=1))
    assert out.status == "invalid_input"
    assert "list_documents" in json.loads(out.content)["error"]


def test_argument_rules():
    with pytest.raises(ValidationError):
        SearchArgs(query="   ")
    with pytest.raises(ValidationError):
        SearchArgs(query="x", top_k=11)
    with pytest.raises(ValidationError):
        SearchArgs(query="x", page_from=5, page_to=1)
    with pytest.raises(ValidationError):
        SectionArgs(document_id=1, page_start=1, page_end=4)  # more than 3 pages
    with pytest.raises(ValidationError):
        SearchArgs(query="x", unexpected="field")
    with pytest.raises(ValidationError):
        ClarificationArgs(question="")


async def test_executor_reports_invalid_arguments_without_running_the_tool(tools):
    outcome, attempts, _ = await execute_tool(ctx(), tools, "search_documents", {"top_k": 3}, {})
    assert (outcome.status, outcome.is_error, attempts) == ("invalid_input", True, 0)
    outcome, _, _ = await execute_tool(ctx(), tools, "delete_everything", {}, {})
    assert "unknown tool" in json.loads(outcome.content)["error"]


async def test_executor_retries_a_timeout_once_and_recovers(tools):
    outcome, attempts, retries = await execute_tool(
        ctx(),
        tools,
        "search_documents",
        {"query": "four functions"},
        {"search_documents": "timeout_once"},
    )
    assert (outcome.status, attempts) == ("ok", 2)
    assert retries == ["timed out after 1 s"]


async def test_executor_gives_up_after_one_retry(tools):
    outcome, attempts, retries = await execute_tool(
        ctx(),
        tools,
        "search_documents",
        {"query": "four functions"},
        {"search_documents": "error"},
    )
    assert (outcome.status, outcome.is_error, attempts) == ("error", True, 2)
    assert json.loads(outcome.content)["attempts"] == 2


async def test_executor_does_not_retry_without_time_for_it(tools):
    settings = get_settings()
    outcome, attempts, _ = await execute_tool(
        ctx(remaining=settings.finalize_reserve_s),
        tools,
        "search_documents",
        {"query": "x"},
        {"search_documents": "error"},
    )
    assert (outcome.status, attempts) == ("error", 1)


def test_limits():
    s = get_settings()
    assert limit_before_tool(ctx()) is None
    assert "tool calls" in limit_before_tool(ctx(tool_calls=s.max_tool_calls))
    assert "time limit" in limit_before_tool(ctx(remaining=s.finalize_reserve_s))
    assert "model turns" in limit_after_tool(ctx(model_turns=s.max_model_turns - 1))
