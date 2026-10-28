"""Upload through the API, ingest with the real worker code and model, then search."""

import asyncio
import os

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db import open_pool
from app.embeddings import Embedder
from app.ingest import jobs
from app.worker import process
from tests.conftest import TEST_DATABASE_URL, make_pdf, needs_db, needs_model, reset_schema

pytestmark = [needs_db, needs_model]

RMF_PAGE = (
    "The AI RMF Core is composed of four functions: GOVERN, MAP, MEASURE, and MANAGE. "
    "Each of these high-level functions is broken down into categories and subcategories."
)
MEMO_PAGE = (
    "Within 180 days of the issuance of this memorandum, each CFO Act agency must develop "
    "an AI Strategy for identifying and removing barriers to the responsible use of AI."
)


def ingest_all() -> None:
    """Run the worker's own claim-and-process step until no job is left."""

    async def run() -> None:
        settings = get_settings()
        embedder = Embedder(
            settings.embed_model, settings.fastembed_cache_path, 2, settings.embed_batch_size
        )
        pool = await open_pool(TEST_DATABASE_URL, max_size=2)
        try:
            while True:
                async with pool.connection() as conn:
                    job = await jobs.claim_next(conn, "test", 60, 3)
                if job is None:
                    return
                await process(pool, embedder, settings, job, "test")
        finally:
            await pool.close()

    asyncio.run(run())


@pytest.fixture
def client():
    reset_schema()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def upload(client, name: str, pages: list[str], title: str) -> int:
    r = client.post(
        "/api/documents", files={"file": (name, make_pdf(pages))}, data={"title": title}
    )
    assert r.status_code == 202, r.text
    return r.json()["id"]


def test_uploaded_pdf_becomes_searchable_with_page_numbers(client):
    rmf = upload(client, "rmf.pdf", ["Cover page.", RMF_PAGE], "NIST AI RMF")
    ingest_all()

    doc = client.get(f"/api/documents/{rmf}").json()
    assert (doc["status"], doc["page_count"]) == ("ready", 2)
    assert doc["chunk_count"] >= 2

    r = client.post("/api/search", json={"query": "What are the four functions of the core?"})
    assert r.status_code == 200
    top = r.json()["hits"][0]
    assert (top["document_id"], top["page_no"]) == (rmf, 2)
    assert "GOVERN, MAP, MEASURE, and MANAGE" in top["text"]


@pytest.mark.skipif(not os.environ.get("TEST_REDIS_URL"), reason="TEST_REDIS_URL is not set")
def test_repeat_search_is_cached_until_the_corpus_changes(client):
    upload(client, "rmf.pdf", [RMF_PAGE], "NIST AI RMF")
    ingest_all()
    query = {"query": "AI strategy deadline for agencies"}
    assert client.post("/api/search", json=query).json()["cache"] == "miss"
    assert client.post("/api/search", json=query).json()["cache"] == "hit"

    # Publishing another document bumps the corpus version, so the old entry is never read.
    memo = upload(client, "memo.pdf", [MEMO_PAGE], "OMB M-25-21")
    ingest_all()
    fresh = client.post("/api/search", json=query).json()
    assert fresh["cache"] == "miss"
    assert fresh["hits"][0]["document_id"] == memo


def test_search_validates_its_input(client):
    assert client.post("/api/search", json={"query": ""}).status_code == 422
    assert client.post("/api/search", json={"query": "   "}).status_code == 422
    assert client.post("/api/search", json={"query": "x", "top_k": 50}).status_code == 422
    bad_range = {"query": "x", "page_from": 5, "page_to": 2}
    assert client.post("/api/search", json=bad_range).status_code == 422


def test_search_on_empty_corpus_returns_no_hits(client):
    r = client.post("/api/search", json={"query": "anything"})
    assert r.status_code == 200
    assert r.json()["hits"] == []
