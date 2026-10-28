"""Ingestion job state against a real PostgreSQL: claim, lease, publish, failure."""

import numpy as np
import psycopg
import pytest
from pgvector.psycopg import register_vector_async

from app.db import migrate
from app.ingest import jobs
from tests.conftest import TEST_DATABASE_URL, needs_db, reset_schema

pytestmark = needs_db


@pytest.fixture
async def conn():
    reset_schema()
    await migrate(TEST_DATABASE_URL)
    async with await psycopg.AsyncConnection.connect(TEST_DATABASE_URL, autocommit=True) as c:
        await register_vector_async(c)
        yield c


async def add_document(conn, sha: str, title: str = "Doc") -> int:
    cur = await conn.execute(
        "INSERT INTO documents (title, filename, sha256, byte_size) VALUES (%s, %s, %s, 3)"
        " RETURNING id",
        (title, f"{sha}.pdf", sha),
    )
    doc_id = (await cur.fetchone())[0]
    await conn.execute(
        "INSERT INTO document_files (document_id, content) VALUES (%s, %s)", (doc_id, b"pdf")
    )
    return doc_id


def chunk(page_no: int, index: int) -> jobs.ChunkRow:
    return jobs.ChunkRow(page_no, index, "text", "Doc | page 1\ntext", 1, np.ones(384, "float32"))


async def status_of(conn, doc_id: int) -> tuple:
    cur = await conn.execute(
        "SELECT status, lease_owner, attempts, page_count FROM documents WHERE id = %s", (doc_id,)
    )
    return await cur.fetchone()


async def test_claim_takes_oldest_queued_and_leases_it(conn):
    first = await add_document(conn, "a")
    await add_document(conn, "b")
    job = await jobs.claim_next(conn, "w1", lease_seconds=60, max_attempts=3)
    assert job == jobs.Job(first, "Doc", 1)
    assert await status_of(conn, first) == ("processing", "w1", 1, None)


async def test_a_leased_job_is_not_claimed_twice(conn):
    await add_document(conn, "a")
    assert await jobs.claim_next(conn, "w1", 60, 3) is not None
    assert await jobs.claim_next(conn, "w2", 60, 3) is None


async def test_expired_lease_is_reclaimed_by_another_worker(conn):
    doc = await add_document(conn, "a")
    await jobs.claim_next(conn, "w1", 60, 3)
    await conn.execute("UPDATE documents SET lease_until = now() - interval '1 second'")
    job = await jobs.claim_next(conn, "w2", 60, 3)
    assert job.document_id == doc and job.attempts == 2


async def test_publish_writes_everything_and_bumps_corpus_version(conn):
    doc = await add_document(conn, "a")
    await jobs.claim_next(conn, "w1", 60, 3)
    ok = await jobs.publish(
        conn, doc, "w1", [(1, "page one"), (2, "page two")], [chunk(1, 0), chunk(2, 0)]
    )
    assert ok
    assert await status_of(conn, doc) == ("ready", None, 1, 2)
    cur = await conn.execute("SELECT count(*) FROM chunks WHERE document_id = %s", (doc,))
    assert (await cur.fetchone())[0] == 2
    cur = await conn.execute("SELECT version FROM corpus_state")
    assert (await cur.fetchone())[0] == 1


async def test_publish_after_losing_the_lease_writes_nothing(conn):
    doc = await add_document(conn, "a")
    await jobs.claim_next(conn, "w1", 60, 3)
    await conn.execute("UPDATE documents SET lease_until = now() - interval '1 second'")
    await jobs.claim_next(conn, "w2", 60, 3)
    assert not await jobs.publish(conn, doc, "w1", [(1, "x")], [chunk(1, 0)])
    cur = await conn.execute("SELECT count(*) FROM pages")
    assert (await cur.fetchone())[0] == 0


async def test_transient_failure_requeues_then_gives_up(conn):
    doc = await add_document(conn, "a")
    job = await jobs.claim_next(conn, "w1", 60, 2)
    assert await jobs.record_failure(conn, doc, "w1", "boom", False, job.attempts, 2) == "queued"
    job = await jobs.claim_next(conn, "w1", 60, 2)
    assert await jobs.record_failure(conn, doc, "w1", "boom", False, job.attempts, 2) == "failed"
    assert await jobs.claim_next(conn, "w1", 60, 2) is None


async def test_permanent_failure_fails_at_once(conn):
    doc = await add_document(conn, "a")
    job = await jobs.claim_next(conn, "w1", 60, 3)
    assert await jobs.record_failure(conn, doc, "w1", "bad", True, job.attempts, 3) == "failed"


async def test_crashed_worker_on_last_attempt_is_failed(conn):
    doc = await add_document(conn, "a")
    await jobs.claim_next(conn, "w1", 60, 1)
    await conn.execute("UPDATE documents SET lease_until = now() - interval '1 second'")
    assert await jobs.fail_exhausted(conn, 1) == 1
    assert (await status_of(conn, doc))[0] == "failed"
