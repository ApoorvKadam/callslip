"""Hybrid search SQL against a real PostgreSQL, with hand-made vectors so ranks are predictable."""

import numpy as np
import psycopg
import pytest
from pgvector.psycopg import register_vector_async

from app.db import migrate, open_pool
from app.retrieval.search import SearchFilters, hybrid_search
from tests.conftest import TEST_DATABASE_URL, needs_db, reset_schema

pytestmark = needs_db


def axis(i: int) -> np.ndarray:
    """A unit vector along one axis: cosine distance 0 to itself, 1 to every other axis."""
    v = np.zeros(384, dtype=np.float32)
    v[i] = 1.0
    return v


def blend(i: int, j: int, weight: float) -> np.ndarray:
    v = (1 - weight) * axis(i) + weight * axis(j)
    return (v / np.linalg.norm(v)).astype(np.float32)


@pytest.fixture
async def pool():
    reset_schema()
    await migrate(TEST_DATABASE_URL)
    async with await psycopg.AsyncConnection.connect(TEST_DATABASE_URL, autocommit=True) as c:
        await register_vector_async(c)

        async def doc(title: str, status: str = "ready") -> int:
            cur = await c.execute(
                "INSERT INTO documents (title, filename, sha256, byte_size, status)"
                " VALUES (%s, %s, %s, 1, %s) RETURNING id",
                (title, f"{title}.pdf", title, status),
            )
            return (await cur.fetchone())[0]

        async def chunk(doc_id: int, page: int, text: str, vec: np.ndarray) -> None:
            await c.execute(
                "INSERT INTO chunks (document_id, page_no, chunk_index, text, search_text,"
                " token_count, embedding) VALUES (%s, %s, 0, %s, %s, 1, %s)",
                (doc_id, page, text, text, vec),
            )

        rmf = await doc("rmf")
        memo = await doc("memo")
        draft = await doc("draft", status="processing")
        # Matches the query by meaning and by words.
        await chunk(rmf, 25, "The core has four functions: govern, map, measure, manage.", axis(0))
        # Close in meaning only.
        await chunk(
            rmf, 30, "Risk management activities are organized at a high level.", blend(0, 1, 0.3)
        )
        # Same words only.
        await chunk(
            memo, 5, "Agencies must govern AI functions through a governance board.", axis(2)
        )
        # Neither.
        await chunk(memo, 9, "Procurement timelines for contracts.", axis(3))
        # Would match perfectly, but its document is not ready.
        await chunk(draft, 1, "Four functions govern map measure manage.", axis(0))

    p = await open_pool(TEST_DATABASE_URL, max_size=2)
    yield p, {"rmf": rmf, "memo": memo}
    await p.close()


async def test_passage_found_by_both_searches_ranks_first(pool):
    p, _ = pool
    hits = await hybrid_search(p, "four functions govern", axis(0), SearchFilters(), top_k=10)
    assert hits[0].page_no == 25
    assert (hits[0].vector_rank, hits[0].keyword_rank) == (1, 1)
    # Vector ranks 25, 30, then 5 and 9 (equally far); only page 25 has all three words.
    assert [h.page_no for h in hits] == [25, 30, 5, 9]


async def test_documents_not_ready_are_never_returned(pool):
    p, _ = pool
    hits = await hybrid_search(p, "four functions govern", axis(0), SearchFilters(), top_k=10)
    assert all(h.title != "draft" for h in hits)


async def test_keyword_only_and_vector_only_passages_both_appear(pool):
    p, _ = pool
    hits = await hybrid_search(p, "governance board", axis(1), SearchFilters(), top_k=10)
    by_page = {h.page_no: h for h in hits}
    assert by_page[5].keyword_rank is not None
    assert by_page[30].keyword_rank is None and by_page[30].vector_rank is not None


async def test_document_filter(pool):
    p, ids = pool
    hits = await hybrid_search(
        p, "four functions govern", axis(0), SearchFilters(document_ids=(ids["memo"],)), top_k=10
    )
    assert hits and {h.document_id for h in hits} == {ids["memo"]}


async def test_page_range_filter(pool):
    p, _ = pool
    hits = await hybrid_search(
        p, "four functions", axis(0), SearchFilters(page_from=6, page_to=40), top_k=10
    )
    assert sorted(h.page_no for h in hits) == [9, 25, 30]


async def test_top_k_limits_results(pool):
    p, _ = pool
    hits = await hybrid_search(p, "four functions", axis(0), SearchFilters(), top_k=2)
    assert len(hits) == 2


async def test_empty_filter_result_is_an_empty_list(pool):
    p, _ = pool
    hits = await hybrid_search(p, "four functions", axis(0), SearchFilters(page_from=500), top_k=5)
    assert hits == []


async def test_a_private_document_is_searched_only_for_its_owner(pool):
    p, _ = pool
    async with p.connection() as conn:
        cur = await conn.execute(
            "INSERT INTO users (email, password_hash) VALUES ('a@x.edu', 'x'), ('b@x.edu', 'x')"
            " RETURNING id"
        )
        owner, other = [r[0] for r in await cur.fetchall()]
        cur = await conn.execute(
            "INSERT INTO documents (title, filename, sha256, byte_size, status, owner_user_id)"
            " VALUES ('notes', 'notes.pdf', 'notes', 1, 'ready', %s) RETURNING id",
            (owner,),
        )
        notes = (await cur.fetchone())[0]
        await conn.execute(
            "INSERT INTO chunks (document_id, page_no, chunk_index, text, search_text,"
            " token_count, embedding) VALUES (%s, 1, 0, 'Private lab notes.', 'Private lab notes.',"
            " 1, %s)",
            (notes, axis(7)),
        )

    def found(viewer):
        return hybrid_search(p, "private lab notes", axis(7), SearchFilters(viewer=viewer), 10)

    assert notes in {h.document_id for h in await found(owner)}
    assert notes not in {h.document_id for h in await found(other)}
    assert notes not in {h.document_id for h in await found(None)}
