"""Ingestion job state in PostgreSQL.

The `documents` row is the job. A worker claims one with a time-limited lease, processes it
outside any transaction, then publishes pages and chunks in one transaction, but only if it
still owns the lease. A crashed worker's lease expires and another worker reclaims the job.
"""

from dataclasses import dataclass

import numpy as np
from psycopg import AsyncConnection


@dataclass(frozen=True)
class Job:
    document_id: int
    title: str
    attempts: int


@dataclass(frozen=True)
class ChunkRow:
    page_no: int
    chunk_index: int
    text: str
    search_text: str
    token_count: int
    embedding: np.ndarray


async def fail_exhausted(conn: AsyncConnection, max_attempts: int) -> int:
    """Expired leases that used every attempt become `failed` instead of retrying forever."""
    cur = await conn.execute(
        """
        UPDATE documents
           SET status = 'failed', lease_owner = NULL, lease_until = NULL, updated_at = now(),
               error = coalesce(error, 'processing did not finish') || ' (gave up after '
                       || attempts || ' attempts)'
         WHERE status = 'processing' AND lease_until < now() AND attempts >= %(max)s
        """,
        {"max": max_attempts},
    )
    return cur.rowcount


async def claim_next(
    conn: AsyncConnection, owner: str, lease_seconds: int, max_attempts: int
) -> Job | None:
    """Atomically take the oldest queued job, or one whose lease expired, and lease it."""
    cur = await conn.execute(
        """
        UPDATE documents
           SET status = 'processing', lease_owner = %(owner)s,
               lease_until = now() + %(lease)s * interval '1 second',
               attempts = attempts + 1, updated_at = now()
         WHERE id = (
               SELECT id FROM documents
                WHERE (status = 'queued'
                       OR (status = 'processing' AND lease_until < now()))
                  AND attempts < %(max)s
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1)
        RETURNING id, title, attempts
        """,
        {"owner": owner, "lease": lease_seconds, "max": max_attempts},
    )
    row = await cur.fetchone()
    return Job(*row) if row else None


async def load_pdf(conn: AsyncConnection, document_id: int) -> bytes:
    cur = await conn.execute(
        "SELECT content FROM document_files WHERE document_id = %s", (document_id,)
    )
    row = await cur.fetchone()
    if row is None:
        raise LookupError(f"document {document_id} has no stored file")
    return bytes(row[0])


async def publish(
    conn: AsyncConnection,
    document_id: int,
    owner: str,
    pages: list[tuple[int, str]],
    chunks: list[ChunkRow],
) -> bool:
    """Write pages and chunks and mark the document ready, in one transaction.

    Returns False, writing nothing, if this worker no longer owns the lease.
    """
    async with conn.transaction():
        cur = await conn.execute(
            "SELECT 1 FROM documents WHERE id = %s AND status = 'processing'"
            " AND lease_owner = %s FOR UPDATE",
            (document_id, owner),
        )
        if await cur.fetchone() is None:
            return False
        # Idempotent: a reclaimed job may have published partially before; start clean.
        await conn.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
        await conn.execute("DELETE FROM pages WHERE document_id = %s", (document_id,))
        async with conn.cursor() as c:
            await c.executemany(
                "INSERT INTO pages (document_id, page_no, text) VALUES (%s, %s, %s)",
                [(document_id, page_no, text) for page_no, text in pages],
            )
            await c.executemany(
                "INSERT INTO chunks (document_id, page_no, chunk_index, text, search_text,"
                " token_count, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [
                    (
                        document_id,
                        ch.page_no,
                        ch.chunk_index,
                        ch.text,
                        ch.search_text,
                        ch.token_count,
                        ch.embedding,
                    )
                    for ch in chunks
                ],
            )
        await conn.execute(
            "UPDATE documents SET status = 'ready', page_count = %s, error = NULL,"
            " lease_owner = NULL, lease_until = NULL, updated_at = now() WHERE id = %s",
            (len(pages), document_id),
        )
        await conn.execute("UPDATE corpus_state SET version = version + 1 WHERE id = 1")
    return True


async def record_failure(
    conn: AsyncConnection,
    document_id: int,
    owner: str,
    error: str,
    permanent: bool,
    attempts: int,
    max_attempts: int,
) -> str:
    """Release the lease: `failed` if permanent or out of attempts, else back to `queued`."""
    status = "failed" if permanent or attempts >= max_attempts else "queued"
    await conn.execute(
        "UPDATE documents SET status = %s, error = %s, lease_owner = NULL, lease_until = NULL,"
        " updated_at = now() WHERE id = %s AND lease_owner = %s",
        (status, error[:500], document_id, owner),
    )
    return status
