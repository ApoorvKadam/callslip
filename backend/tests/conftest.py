"""Shared test setup.

Database tests run against a real PostgreSQL with pgvector, named by TEST_DATABASE_URL
(CI provides one as a service container; locally, point it at the Compose database).
They are skipped when it is not set. Each test module starts from an empty schema.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

import psycopg
import pytest
from fpdf import FPDF

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if TEST_DATABASE_URL:
    # The app reads its settings from the environment; point it at the test database.
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    # With TEST_REDIS_URL the app uses a real Redis; otherwise an address where none listens.
    os.environ["REDIS_URL"] = os.environ.get("TEST_REDIS_URL", "redis://127.0.0.1:1/0")

needs_db = pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not set")

# The API loads the local embedding model at startup; CI and developers download it once into
# FASTEMBED_CACHE_PATH (see README). Tests that start the app need it.
MODEL_CACHE = os.environ.get("FASTEMBED_CACHE_PATH", "/opt/models")


def _model_present(path: str) -> bool:
    return Path(path).exists() and any(Path(path).rglob("tokenizer.json"))


needs_model = pytest.mark.skipif(
    not _model_present(MODEL_CACHE), reason=f"embedding model not found in {MODEL_CACHE}"
)


def reset_schema() -> None:
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")


def make_pdf(pages: list[str]) -> bytes:
    """A real text-layer PDF with one string per page. The creation date is fixed, so the same
    pages always give the same bytes, as duplicate detection expects."""
    pdf = FPDF()
    pdf.set_creation_date(datetime(2026, 1, 1, tzinfo=UTC))
    pdf.set_font("Helvetica", size=11)
    for text in pages:
        pdf.add_page()
        if text:
            pdf.multi_cell(0, 6, text)
    return bytes(pdf.output())
