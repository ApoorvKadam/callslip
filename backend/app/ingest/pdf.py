"""Page-by-page text extraction with pypdf.

Page numbers are physical PDF pages, 1-based, which is what a PDF viewer opens with `#page=N`.
The PDF's own bookmarks, when it has them, are kept as an outline: section titles with the
physical page each one opens at.
Text is kept exactly as extracted except that whitespace runs collapse to one space; OCR noise
in scanned-then-OCRed PDFs is preserved, never repaired, because it is quoted back as evidence.

Parsing untrusted PDFs can take unbounded time or memory (compression bombs, pathological
content streams), so it runs in a child process with a wall-clock timeout, a memory cap and a
cap on extracted text. A child that runs over is killed and the document is rejected.
"""

import io
import multiprocessing
import re
import resource
from dataclasses import dataclass
from multiprocessing.connection import Connection

from pypdf import PdfReader
from pypdf.errors import PdfReadError

_WHITESPACE = re.compile(r"\s+")
_LETTER = re.compile(r"[^\W\d_]")
MAX_OUTLINE = 300


class PdfRejected(Exception):
    """A permanent problem with the file itself: retrying will not help."""


@dataclass(frozen=True)
class Page:
    page_no: int
    text: str


@dataclass(frozen=True)
class ParsedPdf:
    pages: list[Page]
    outline: list[dict]  # {"title", "page", "level"}; empty when the PDF has no bookmarks


def normalize_whitespace(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def _outline(reader: PdfReader) -> list[dict]:
    """The PDF's bookmarks in order, each with the physical page it opens. A broken outline
    is skipped, never a reason to reject the document."""
    entries: list[dict] = []

    def walk(items: list, level: int) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item, level + 1)
                continue
            if len(entries) >= MAX_OUTLINE:
                return
            page = reader.get_destination_page_number(item)
            title = normalize_whitespace(str(item.title or ""))[:200]
            # Entries without a page or without words ("1.", "2.") do not help navigation.
            if page is not None and page >= 0 and _LETTER.search(title):
                entries.append({"title": title, "page": page + 1, "level": level})

    try:
        walk(reader.outline, 0)
    except Exception:
        return []
    return entries


def _extract(content: bytes, max_pages: int, max_chars: int) -> ParsedPdf:
    try:
        reader = PdfReader(io.BytesIO(content))
        # Many public PDFs are "encrypted" only to restrict editing; an empty password opens them.
        if reader.is_encrypted and not reader.decrypt(""):
            raise PdfRejected("password-protected PDFs are not supported")
        page_count = len(reader.pages)
    except PdfReadError as exc:
        raise PdfRejected(f"not a readable PDF: {exc}") from exc

    if page_count == 0:
        raise PdfRejected("the PDF has no pages")
    if page_count > max_pages:
        raise PdfRejected(f"the PDF has {page_count} pages; the limit is {max_pages}")

    pages: list[Page] = []
    total = 0
    for page_no, page in enumerate(reader.pages, start=1):
        text = normalize_whitespace(page.extract_text() or "")
        total += len(text)
        if total > max_chars:
            raise PdfRejected(f"the PDF has more than {max_chars} characters of text")
        pages.append(Page(page_no, text))
    if not any(page.text for page in pages):
        raise PdfRejected("no text layer found (image-only PDF); OCR is not supported")
    return ParsedPdf(pages, _outline(reader))


def _child(content: bytes, max_pages: int, max_chars: int, mem_bytes: int, out: Connection):
    """Runs in the child process: cap memory, extract, send back the result or the error."""
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    try:
        out.send(("ok", _extract(content, max_pages, max_chars)))
    except PdfRejected as exc:
        out.send(("rejected", str(exc)))
    except MemoryError:
        out.send(("rejected", "parsing the PDF needed more memory than allowed"))
    except Exception as exc:  # anything else is reported, not swallowed
        out.send(("error", f"{type(exc).__name__}: {exc}"))


def parse_pdf(
    content: bytes,
    max_pages: int,
    timeout_s: float = 120.0,
    max_chars: int = 5_000_000,
    mem_bytes: int = 768 * 1024 * 1024,
) -> ParsedPdf:
    ctx = multiprocessing.get_context("spawn")
    receive, send = ctx.Pipe(duplex=False)
    proc = ctx.Process(
        target=_child, args=(content, max_pages, max_chars, mem_bytes, send), daemon=True
    )
    proc.start()
    send.close()
    try:
        if not receive.poll(timeout_s):
            raise PdfRejected(f"parsing took longer than {timeout_s:g} seconds")
        status, payload = receive.recv()
    except EOFError:
        raise PdfRejected(
            "the parser stopped unexpectedly (out of memory or invalid file)"
        ) from None
    finally:
        if proc.is_alive():
            proc.kill()
        proc.join(timeout=5)
        receive.close()

    if status == "ok":
        return payload
    if status == "rejected":
        raise PdfRejected(payload)
    raise RuntimeError(payload)
