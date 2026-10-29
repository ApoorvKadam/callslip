"""Document upload, listing and file download.

Upload validates the file and stores it with status `queued`; the worker does the parsing,
so the request returns quickly (202) and the UI follows the status. A signed-in user's upload
is theirs alone; without signing in, an upload joins the shared collection. Every read below
shows the shared collection plus the viewer's own documents, and nothing else.
"""

import hashlib
import re
from pathlib import PurePath
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile
from psycopg import errors
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel

from app.api.auth import Viewer, take_attempt
from app.api.deps import get_pool, settings
from app.config import Settings

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Stored file names are reduced to a safe ASCII set: they end up in a response header.
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._ -]+")


def safe_filename(name: str | None) -> str:
    base = PurePath(name or "").name
    cleaned = _UNSAFE_FILENAME_CHARS.sub("_", base).strip(" .")[:200]
    return cleaned if cleaned.lower().endswith(".pdf") else f"{cleaned or 'document'}.pdf"


_SELECT = """
    SELECT d.id, d.title, d.filename, d.status, d.error, d.page_count, d.byte_size,
           d.created_at, d.updated_at, d.owner_user_id IS NOT NULL AS private,
           (SELECT count(*) FROM chunks c WHERE c.document_id = d.id) AS chunk_count
      FROM documents d
"""
VISIBLE = " (d.owner_user_id IS NULL OR d.owner_user_id = %s) "


class DocumentOut(BaseModel):
    id: int
    title: str
    filename: str
    status: str
    error: str | None
    page_count: int | None
    byte_size: int
    chunk_count: int
    private: bool  # the viewer's own upload, not in the shared collection
    created_at: str
    updated_at: str


def _out(row: dict) -> DocumentOut:
    return DocumentOut(
        **{
            **row,
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }
    )


@router.post("", status_code=202)
async def upload_document(
    pool: Annotated[AsyncConnectionPool, Depends(get_pool)],
    cfg: Annotated[Settings, Depends(settings)],
    file: Annotated[UploadFile, File(description="A text-based PDF")],
    user: Viewer,
    request: Request,
    title: Annotated[str | None, Form(max_length=300)] = None,
) -> DocumentOut:
    if user is None and not cfg.allow_guest_uploads:
        raise HTTPException(401, "Sign in to upload PDFs.")
    if cfg.upload_limit > 0:
        address = request.client.host if request.client else "unknown"
        key = "upload:addr:" + hashlib.sha256(address.encode()).hexdigest()
        wait = await take_attempt(
            request.app.state.redis, key, cfg.upload_limit, cfg.upload_window_s
        )
        if wait:
            raise HTTPException(
                429,
                f"Too many uploads from this address. Try again in {-(-wait // 60)} min.",
                headers={"Retry-After": str(wait)},
            )
    limit = cfg.max_upload_mb * 1024 * 1024
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(413, f"File is larger than {cfg.max_upload_mb} MB.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(415, "Only PDF files are accepted.")
    try:
        return await store_pdf(pool, content, file.filename, title, user)
    except AlreadyUploaded as e:
        raise HTTPException(
            409, {"message": "This PDF is already uploaded.", "document_id": e.document_id}
        ) from None


class AlreadyUploaded(Exception):
    def __init__(self, document_id: int):
        self.document_id = document_id


async def store_pdf(
    pool: AsyncConnectionPool,
    content: bytes,
    original_name: str | None,
    title: str | None,
    owner: int | None,
) -> DocumentOut:
    """Store a checked PDF as a queued document for the worker to parse. With no owner it
    joins the shared collection. The same bytes twice for one owner raise AlreadyUploaded."""
    filename = safe_filename(original_name)
    # The title is display text (never a header), so it keeps the original characters.
    original_stem = PurePath(original_name or "").stem
    # One line: a title with line breaks could pass for more entries in the agent's document list.
    clean_title = " ".join((title or "").split()) or original_stem or PurePath(filename).stem
    clean_title = " ".join(clean_title.split())[:300]
    digest = hashlib.sha256(content).hexdigest()
    try:
        async with pool.connection() as conn, conn.transaction():
            cur = conn.cursor(row_factory=dict_row)
            await cur.execute(
                "INSERT INTO documents (title, filename, sha256, byte_size, owner_user_id)"
                " VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (clean_title, filename, digest, len(content), owner),
            )
            doc_id = (await cur.fetchone())["id"]
            await cur.execute(
                "INSERT INTO document_files (document_id, content) VALUES (%s, %s)",
                (doc_id, content),
            )
            await cur.execute(_SELECT + " WHERE d.id = %s", (doc_id,))
            return _out(await cur.fetchone())
    except errors.UniqueViolation:
        async with pool.connection() as conn:
            cur = await conn.execute(
                "SELECT id FROM documents WHERE sha256 = %s"
                " AND owner_user_id IS NOT DISTINCT FROM %s",
                (digest, owner),
            )
            existing = await cur.fetchone()
        raise AlreadyUploaded(existing[0]) from None


@router.get("")
async def list_documents(
    pool: Annotated[AsyncConnectionPool, Depends(get_pool)], user: Viewer
) -> list[DocumentOut]:
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(_SELECT + " WHERE" + VISIBLE + "ORDER BY d.created_at, d.id", (user,))
        return [_out(row) for row in await cur.fetchall()]


@router.get("/{document_id}")
async def get_document(
    document_id: int, pool: Annotated[AsyncConnectionPool, Depends(get_pool)], user: Viewer
) -> DocumentOut:
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(_SELECT + " WHERE d.id = %s AND" + VISIBLE, (document_id, user))
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(404, "Document not found.")
    return _out(row)


@router.get("/{document_id}/file")
async def get_document_file(
    document_id: int, pool: Annotated[AsyncConnectionPool, Depends(get_pool)], user: Viewer
) -> Response:
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT d.filename, f.content FROM documents d"
            " JOIN document_files f ON f.document_id = d.id WHERE d.id = %s AND" + VISIBLE,
            (document_id, user),
        )
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(404, "Document not found.")
    filename, content = row
    # Inline so the browser's PDF viewer opens it; the UI appends #page=N to jump to a page.
    return Response(
        bytes(content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename(filename)}"',
            "X-Content-Type-Options": "nosniff",
            # A private document must not be kept by shared caches or proxies.
            "Cache-Control": "private, no-store",
        },
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int, pool: Annotated[AsyncConnectionPool, Depends(get_pool)], user: Viewer
) -> None:
    """Delete one of your own uploads: its pages, passages and file go with it. Shared documents
    cannot be deleted here, and another user's document is not found."""
    if user is None:
        raise HTTPException(401, "Sign in to delete your documents.")
    async with pool.connection() as conn, conn.transaction():
        cur = await conn.execute(
            "SELECT status FROM documents WHERE id = %s AND owner_user_id = %s FOR UPDATE",
            (document_id, user),
        )
        row = await cur.fetchone()
        if row is None:
            raise HTTPException(404, "Document not found.")
        if row[0] in ("queued", "processing"):
            raise HTTPException(409, "The document is still being processed; try again shortly.")
        await conn.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        # Cached searches name the corpus version, so none that included it is read again.
        await conn.execute("UPDATE corpus_state SET version = version + 1 WHERE id = 1")
