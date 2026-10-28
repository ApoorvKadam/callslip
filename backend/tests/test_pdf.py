import pytest
from fpdf import FPDF

from app.ingest.pdf import PdfRejected, parse_pdf
from tests.conftest import make_pdf


def test_pages_keep_physical_numbers_and_text():
    pages = parse_pdf(make_pdf(["First page text.", "", "Third page text."]), max_pages=10).pages
    assert [p.page_no for p in pages] == [1, 2, 3]
    assert pages[0].text == "First page text."
    assert pages[1].text == ""
    assert pages[2].text == "Third page text."


def test_whitespace_is_collapsed():
    pages = parse_pdf(make_pdf(["Line one\nline two   and three"]), max_pages=10).pages
    assert pages[0].text == "Line one line two and three"


def test_pdf_without_any_text_is_rejected():
    with pytest.raises(PdfRejected, match="no text layer"):
        parse_pdf(make_pdf(["", ""]), max_pages=10)


def test_page_limit():
    with pytest.raises(PdfRejected, match="limit is 2"):
        parse_pdf(make_pdf(["a", "b", "c"]), max_pages=2)


def test_garbage_is_rejected():
    with pytest.raises(PdfRejected, match="not a readable PDF"):
        parse_pdf(b"%PDF-1.7 this is not really a pdf", max_pages=10)


def test_parsing_that_runs_too_long_is_stopped_and_rejected():
    # A timeout shorter than starting the child process: the parser is killed and rejected.
    with pytest.raises(PdfRejected, match="took longer than"):
        parse_pdf(make_pdf(["Text."]), max_pages=10, timeout_s=0.001)


def test_text_cap_rejects_huge_extractions():
    with pytest.raises(PdfRejected, match="more than 10 characters"):
        parse_pdf(make_pdf(["This page has far more than ten characters."]), 10, max_chars=10)


def test_bookmarks_become_the_outline_with_physical_pages():
    pdf = FPDF()
    pdf.set_font("Helvetica", size=11)
    for title, level in [("1. Introduction", 0), ("2. Risks", 0), ("2.1. Data Privacy", 1)]:
        pdf.add_page()
        pdf.start_section(title, level=level)
        pdf.multi_cell(0, 6, f"Text of {title}.")
    parsed = parse_pdf(bytes(pdf.output()), max_pages=10)
    assert parsed.outline == [
        {"title": "1. Introduction", "page": 1, "level": 0},
        {"title": "2. Risks", "page": 2, "level": 0},
        {"title": "2.1. Data Privacy", "page": 3, "level": 1},
    ]


def test_a_pdf_without_bookmarks_has_an_empty_outline():
    assert parse_pdf(make_pdf(["Text."]), max_pages=10).outline == []
