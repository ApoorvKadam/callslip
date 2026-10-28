import pytest

from app.ingest.pdf import PdfRejected, extract_pages
from tests.conftest import make_pdf


def test_pages_keep_physical_numbers_and_text():
    pages = extract_pages(make_pdf(["First page text.", "", "Third page text."]), max_pages=10)
    assert [p.page_no for p in pages] == [1, 2, 3]
    assert pages[0].text == "First page text."
    assert pages[1].text == ""
    assert pages[2].text == "Third page text."


def test_whitespace_is_collapsed():
    pages = extract_pages(make_pdf(["Line one\nline two   and three"]), max_pages=10)
    assert pages[0].text == "Line one line two and three"


def test_pdf_without_any_text_is_rejected():
    with pytest.raises(PdfRejected, match="no text layer"):
        extract_pages(make_pdf(["", ""]), max_pages=10)


def test_page_limit():
    with pytest.raises(PdfRejected, match="limit is 2"):
        extract_pages(make_pdf(["a", "b", "c"]), max_pages=2)


def test_garbage_is_rejected():
    with pytest.raises(PdfRejected, match="not a readable PDF"):
        extract_pages(b"%PDF-1.7 this is not really a pdf", max_pages=10)
