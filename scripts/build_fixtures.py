"""Render the synthetic test documents in corpus/fixtures/*.md to PDFs in corpus/pdfs/.

    cd backend && uv run python ../scripts/build_fixtures.py

The first line ("# ...") becomes the title; blank-line-separated paragraphs become text. The
creation date is fixed so the same source always gives the same bytes (and SHA-256).
"""

from datetime import UTC, datetime
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
FIXED_DATE = datetime(2026, 10, 27, tzinfo=UTC)


def render(source: Path, target: Path) -> None:
    lines = source.read_text(encoding="utf-8").strip().split("\n")
    title = lines[0].removeprefix("# ").strip()
    paragraphs = [p.strip() for p in "\n".join(lines[1:]).split("\n\n") if p.strip()]

    pdf = FPDF()
    pdf.set_creation_date(FIXED_DATE)
    pdf.set_title(title)
    pdf.set_author("Synthetic test fixture")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 7, title)
    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    for paragraph in paragraphs:
        pdf.multi_cell(0, 6, paragraph.replace("\n", " "))
        pdf.ln(2)
    target.write_bytes(bytes(pdf.output()))


def main() -> None:
    for source in sorted((ROOT / "corpus" / "fixtures").glob("*.md")):
        target = ROOT / "corpus" / "pdfs" / f"{source.stem}.pdf"
        render(source, target)
        print(f"{source.name} -> {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
