"""Accounts and personal documents, through the real app: who can see what."""

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.agent.tools import ListArgs, Tools
from app.api.auth import AUTH_COOKIE, check_password, hash_password
from app.db import open_pool
from app.runs.store import RunStore
from tests.conftest import TEST_DATABASE_URL, make_pdf, needs_db, needs_model, reset_schema

pytestmark = [needs_db, needs_model]
PASSWORD = "correct horse battery"


@pytest.fixture
def client():
    reset_schema()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def sign_up(client: TestClient, email: str) -> None:
    client.cookies.clear()
    r = client.post("/api/auth/register", json={"email": email, "password": PASSWORD})
    assert r.status_code == 201


def upload(client: TestClient, text: str) -> int:
    pdf = make_pdf([text])
    r = client.post("/api/documents", files={"file": ("notes.pdf", pdf, "application/pdf")})
    assert r.status_code == 202, r.text
    return r.json()["id"]


def test_passwords_are_hashed_and_checked():
    stored = hash_password(PASSWORD)
    assert PASSWORD not in stored and stored.startswith("scrypt$")
    assert check_password(PASSWORD, stored)
    assert not check_password("wrong password", stored)
    assert not check_password(PASSWORD, "not a hash")


def test_sign_up_sign_in_and_out(client):
    sign_up(client, "Ada@NYU.edu")
    cookie = client.cookies.get(AUTH_COOKIE)
    assert cookie and client.get("/api/auth/me").json() == {"email": "Ada@NYU.edu"}

    again = client.post("/api/auth/register", json={"email": "ada@nyu.edu", "password": PASSWORD})
    assert again.status_code == 409  # emails are compared without case

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").json() == {"email": None}

    wrong = client.post("/api/auth/login", json={"email": "ada@nyu.edu", "password": "x" * 12})
    unknown = client.post("/api/auth/login", json={"email": "no@nyu.edu", "password": "x" * 12})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()  # no hint whether the account exists
    ok = client.post("/api/auth/login", json={"email": "ada@nyu.edu", "password": PASSWORD})
    assert ok.status_code == 200 and client.get("/api/auth/me").json()["email"] == "Ada@NYU.edu"


def test_short_passwords_are_refused(client):
    r = client.post("/api/auth/register", json={"email": "b@nyu.edu", "password": "short"})
    assert r.status_code == 422


def test_an_upload_is_private_to_its_owner(client):
    client.cookies.clear()
    shared = upload(client, "Shared policy text.")  # not signed in: the shared collection
    sign_up(client, "ada@nyu.edu")
    mine = upload(client, "Ada's own notes.")

    listed = {d["id"]: d["private"] for d in client.get("/api/documents").json()}
    assert listed == {shared: False, mine: True}
    assert client.get(f"/api/documents/{mine}/file").status_code == 200

    sign_up(client, "bo@nyu.edu")  # another user sees the shared collection only
    assert [d["id"] for d in client.get("/api/documents").json()] == [shared]
    assert client.get(f"/api/documents/{mine}").status_code == 404
    assert client.get(f"/api/documents/{mine}/file").status_code == 404

    client.cookies.clear()  # and so does a visitor who is not signed in
    assert [d["id"] for d in client.get("/api/documents").json()] == [shared]


def test_the_same_pdf_can_be_shared_and_private_once_each(client):
    client.cookies.clear()
    upload(client, "One text.")
    pdf = make_pdf(["One text."])
    again = client.post("/api/documents", files={"file": ("a.pdf", pdf, "application/pdf")})
    assert again.status_code == 409
    sign_up(client, "ada@nyu.edu")
    upload(client, "One text.")  # the same bytes, now as Ada's own copy


async def test_the_agent_lists_only_documents_the_asker_can_see(client):
    sign_up(client, "ada@nyu.edu")
    upload(client, "Ada's own notes.")
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute("UPDATE documents SET status = 'ready', page_count = 1")
        owner = conn.execute("SELECT owner_user_id FROM documents").fetchone()[0]
    pool = await open_pool(TEST_DATABASE_URL, max_size=1)
    try:
        store = RunStore(pool)
        as_owner = await Tools(None, store, owner).list_documents(ListArgs())
        as_visitor = await Tools(None, store, None).list_documents(ListArgs())
    finally:
        await pool.close()
    assert as_owner.status == "ok" and as_visitor.status == "no_results"


def test_a_conversation_belongs_to_the_account_that_started_it(client):
    client.cookies.clear()
    anonymous = client.post("/api/sessions").json()["id"]  # sets this browser's token

    def register(email):  # on the same browser, keeping its token
        r = client.post("/api/auth/register", json={"email": email, "password": PASSWORD})
        assert r.status_code == 201

    register("ada@nyu.edu")
    assert client.get(f"/api/sessions/{anonymous}").status_code == 404
    ada = client.post("/api/sessions").json()["id"]
    assert client.get(f"/api/sessions/{ada}").status_code == 200

    client.post("/api/auth/logout")  # signed out: Ada's answers are out of reach
    assert client.get(f"/api/sessions/{ada}").status_code == 404
    assert client.get(f"/api/sessions/{anonymous}").status_code == 200

    register("bo@nyu.edu")  # another account on the same browser
    assert client.get(f"/api/sessions/{ada}").status_code == 404
    assert client.get(f"/api/sessions/{anonymous}").status_code == 404


def test_a_malformed_browser_token_is_replaced(client):
    client.cookies.clear()
    client.cookies.set("rag_client", "a" * 40 + ":1", path="/api")  # not a token this server made
    r = client.post("/api/sessions")
    assert r.status_code == 201
    assert "rag_client=" in r.headers["set-cookie"]  # a fresh token was issued
