"""Page-by-page text extraction with pypdf.

Page numbers are physical PDF pages, 1-based, which is what a PDF viewer opens with `#page=N`.
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


class PdfRejected(Exception):
    """A permanent problem with the file itself: retrying will not help."""


@dataclass(frozen=True)
class Page:
    page_no: int
    text: str


def normalize_whitespace(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


def _extract(content: bytes, max_pages: int, max_chars: int) -> list[Page]:
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
    return pages


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


def extract_pages(
    content: bytes,
    max_pages: int,
    timeout_s: float = 120.0,
    max_chars: int = 5_000_000,
    mem_bytes: int = 768 * 1024 * 1024,
) -> list[Page]:
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
