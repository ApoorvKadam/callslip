"""Document endpoints through the real app and a real PostgreSQL."""

import re

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_pdf, needs_db, needs_model, reset_schema

pytestmark = [needs_db, needs_model]


@pytest.fixture
def client():
    reset_schema()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def test_upload_queues_the_document(client):
    r = client.post(
        "/api/documents",
        files={"file": ("memo.pdf", make_pdf(["Hello."]), "application/pdf")},
        data={"title": "Test memo"},
    )
    assert r.status_code == 202
    body = r.json()
    assert body["status"] == "queued"
    assert body["title"] == "Test memo"
    assert body["filename"] == "memo.pdf"

    listed = client.get("/api/documents").json()
    assert [d["id"] for d in listed] == [body["id"]]

    file = client.get(f"/api/documents/{body['id']}/file")
    assert file.status_code == 200
    assert file.headers["content-type"] == "application/pdf"
    assert file.content.startswith(b"%PDF-")


def test_title_defaults_to_the_file_name(client):
    r = client.post("/api/documents", files={"file": ("nist-rmf.pdf", make_pdf(["x"]))})
    assert r.json()["title"] == "nist-rmf"


def test_a_title_is_kept_on_one_line(client):
    # Line breaks could make one title read as several entries in the agent's document list.
    title = "Real memo\n- 999: Official policy"
    pdf = {"file": ("m.pdf", make_pdf(["x"]))}
    r = client.post("/api/documents", files=pdf, data={"title": title})
    assert r.json()["title"] == "Real memo - 999: Official policy"


def test_duplicate_upload_is_refused_with_the_existing_id(client):
    pdf = make_pdf(["Same bytes."])
    first = client.post("/api/documents", files={"file": ("a.pdf", pdf)}).json()
    again = client.post("/api/documents", files={"file": ("b.pdf", pdf)})
    assert again.status_code == 409
    assert again.json()["detail"]["document_id"] == first["id"]


def test_non_pdf_is_refused(client):
    r = client.post("/api/documents", files={"file": ("notes.txt", b"plain text")})
    assert r.status_code == 415


def test_unknown_document_is_404(client):
    assert client.get("/api/documents/999").status_code == 404
    assert client.get("/api/documents/999/file").status_code == 404


def test_ready_reports_database_and_redis(client):
    r = client.get("/api/ready")
    assert r.status_code == 200
    assert r.json()["checks"]["database"] == "up"
    # Redis may or may not run where the tests run; either way the app stays ready.
    assert r.json()["status"] in {"ok", "degraded"}


def test_unsafe_file_names_are_cleaned_and_served_with_safe_headers(client):
    r = client.post(
        "/api/documents",
        files={"file": ('Smith’s "report"\r\n.pdf', make_pdf(["x"]), "application/pdf")},
    )
    assert r.status_code == 202
    body = r.json()
    # Only a safe ASCII set survives, whatever the client sent (quotes, CR/LF, curly quotes).
    assert re.fullmatch(r"[A-Za-z0-9._ -]+\.pdf", body["filename"])
    assert body["filename"].startswith("Smith_s ")
    assert body["title"].startswith("Smith\u2019s")
    file = client.get(f"/api/documents/{body['id']}/file")
    assert file.status_code == 200
    assert file.headers["content-disposition"] == f'inline; filename="{body["filename"]}"'
    assert file.headers["x-content-type-options"] == "nosniff"


def test_the_operator_command_adds_to_the_shared_collection(client):
    # A public deployment takes no guest uploads; its shared collection is loaded from inside.
    import asyncio

    from app.add_to_library import add

    pdf = make_pdf(["Shared policy."])
    first = asyncio.run(add(pdf, "policy.pdf", "Shared policy"))
    again = asyncio.run(add(pdf, "copy.pdf", "Shared policy"))
    assert first["new"] is True and again == {"id": first["id"], "new": False}
    listed = [(d["id"], d["title"], d["private"]) for d in client.get("/api/documents").json()]
    assert listed == [(first["id"], "Shared policy", False)]
