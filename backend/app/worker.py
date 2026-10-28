"""Ingestion worker: `python -m app.worker`.

Loop: give up on jobs that ran out of attempts, claim the next job, parse, chunk and embed it
off the event loop, then publish. One job at a time per process; run more containers to scale.
"""

import asyncio
import contextlib
import logging
import os
import signal
import socket
import time
from pathlib import Path

from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from app.config import Settings, get_settings
from app.db import migrate, open_pool
from app.embeddings import Embedder
from app.ingest import jobs
from app.ingest.chunking import chunk_page
from app.ingest.pdf import Page, PdfRejected, parse_pdf
from app.logs import setup_logging

log = logging.getLogger("worker")
HEARTBEAT = Path("/tmp/worker-heartbeat")


async def heartbeat(stop: asyncio.Event, every_s: float = 10.0) -> None:
    """Touch the health-check file while the event loop is alive, including during long jobs
    (parsing runs in a child process and embedding in a thread, so the loop stays free)."""
    while not stop.is_set():
        HEARTBEAT.touch()
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=every_s)


def build_chunks(pages: list[Page], title: str, embedder: Embedder, settings: Settings):
    """Chunk every page and embed the chunks. CPU-bound: called through asyncio.to_thread."""
    rows: list[tuple[int, int, str, str, int]] = []
    for page in pages:
        if not page.text:
            continue
        for index, text in enumerate(
            chunk_page(
                page.text,
                embedder.count_tokens,
                settings.chunk_tokens,
                settings.chunk_overlap_tokens,
            )
        ):
            # The header helps retrieval find a document even when its body text is noisy OCR.
            search_text = f"{title} | page {page.page_no}\n{text}"
            rows.append((page.page_no, index, text, search_text, embedder.count_tokens(text)))
    vectors = embedder.embed_passages([r[3] for r in rows])
    return [
        jobs.ChunkRow(page_no, index, text, search_text, tokens, vector)
        for (page_no, index, text, search_text, tokens), vector in zip(rows, vectors, strict=True)
    ]


async def process(
    pool: AsyncConnectionPool, embedder: Embedder, settings: Settings, job: jobs.Job, owner: str
) -> None:
    started = time.monotonic()
    fields = {"document_id": job.document_id, "attempt": job.attempts}
    try:
        async with pool.connection() as conn:
            content = await jobs.load_pdf(conn, job.document_id)
        parsed = await asyncio.to_thread(parse_pdf, content, settings.max_pages)
        pages = parsed.pages
        chunks = await asyncio.to_thread(build_chunks, pages, job.title, embedder, settings)
        async with pool.connection() as conn:
            published = await jobs.publish(
                conn,
                job.document_id,
                owner,
                [(p.page_no, p.text) for p in pages],
                chunks,
                parsed.outline,
            )
        if published:
            log.info(
                "document ready",
                extra={
                    "fields": {
                        **fields,
                        "pages": len(pages),
                        "chunks": len(chunks),
                        "seconds": round(time.monotonic() - started, 1),
                    }
                },
            )
        else:
            log.warning("lease lost before publish; result discarded", extra={"fields": fields})
    except Exception as exc:  # every failure is recorded on the document, then the loop goes on
        permanent = isinstance(exc, PdfRejected)
        async with pool.connection() as conn:
            status = await jobs.record_failure(
                conn,
                job.document_id,
                owner,
                f"{type(exc).__name__}: {exc}",
                permanent,
                job.attempts,
                settings.max_attempts,
            )
        log.warning(
            "document failed",
            exc_info=not permanent,
            extra={"fields": {**fields, "status": status, "error": str(exc)}},
        )


# Documents whose outline failed to read in this process; retried after a restart.
_outline_failed: set[int] = set()


async def fill_one_outline(pool: AsyncConnectionPool, settings: Settings) -> bool:
    """Read the outline of one document ingested before outlines were kept. Runs only when no
    ingestion job is waiting, so new uploads never wait for it. Returns whether it found one."""
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT id FROM documents WHERE status = 'ready' AND outline IS NULL"
            " AND NOT (id = ANY(%s)) ORDER BY id LIMIT 1",
            (list(_outline_failed),),
        )
        row = await cur.fetchone()
    if row is None:
        return False
    document_id = row[0]
    try:
        async with pool.connection() as conn:
            content = await jobs.load_pdf(conn, document_id)
        parsed = await asyncio.to_thread(parse_pdf, content, settings.max_pages)
    except PdfRejected:
        outline: list[dict] = []  # it will not parse any better next time
    except Exception as exc:
        # Possibly transient: leave it unread, and try again after the next restart.
        _outline_failed.add(document_id)
        log.warning(
            "outline not read", extra={"fields": {"document_id": document_id, "error": str(exc)}}
        )
        return True
    else:
        outline = parsed.outline
    async with pool.connection() as conn:
        await conn.execute(
            "UPDATE documents SET outline = %s WHERE id = %s AND outline IS NULL",
            (Jsonb(outline), document_id),
        )
    return True


async def run() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    owner = f"{socket.gethostname()}:{os.getpid()}"
    await migrate(settings.database_url)
    pool = await open_pool(settings.database_url, max_size=2)
    embedder = await asyncio.to_thread(
        Embedder,
        settings.embed_model,
        settings.fastembed_cache_path,
        settings.embed_threads,
        settings.embed_batch_size,
    )
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    log.info("worker started", extra={"fields": {"owner": owner, "model": settings.embed_model}})
    beat = asyncio.create_task(heartbeat(stop))

    while not stop.is_set():
        async with pool.connection() as conn:
            await jobs.fail_exhausted(conn, settings.max_attempts)
            job = await jobs.claim_next(conn, owner, settings.lease_seconds, settings.max_attempts)
        if job is None:
            if await fill_one_outline(pool, settings):
                continue
            # Sleep until the next poll, waking early on shutdown.
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=settings.worker_poll_seconds)
            continue
        await process(pool, embedder, settings, job, owner)

    await beat
    await pool.close()
    log.info("worker stopped", extra={"fields": {"owner": owner}})


if __name__ == "__main__":
    asyncio.run(run())
