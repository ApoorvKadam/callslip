"""Page-by-page text extraction with pypdf.

Page numbers are physical PDF pages, 1-based, which is what a PDF viewer opens with `#page=N`.
Text is kept exactly as extracted except that whitespace runs collapse to one space; OCR noise
in scanned-then-OCRed PDFs is preserved, never repaired, because it is quoted back as evidence.
"""

import io
import re
from dataclasses import dataclass

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


def extract_pages(content: bytes, max_pages: int) -> list[Page]:
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

    pages = [
        Page(page_no, normalize_whitespace(page.extract_text() or ""))
        for page_no, page in enumerate(reader.pages, start=1)
    ]
    if not any(page.text for page in pages):
        raise PdfRejected("no text layer found (image-only PDF); OCR is not supported")
    return pages
