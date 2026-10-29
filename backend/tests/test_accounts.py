"""Accounts and personal documents, through the real app: who can see what."""

import psycopg
import pytest
from fastapi.testclient import TestClient
from redis import Redis

from app.agent.tools import ListArgs, Tools
from app.api.auth import AUTH_COOKIE, check_password, hash_password
from app.db import open_pool
from app.runs.store import RunStore
from tests.conftest import (
    TEST_DATABASE_URL,
    TEST_REDIS_URL,
    make_pdf,
    needs_db,
    needs_model,
    needs_redis,
    reset_schema,
)

pytestmark = [needs_db, needs_model]
PASSWORD = "correct horse battery"


@pytest.fixture
def client():
    reset_schema()
    clear_sign_in_counts()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def clear_sign_in_counts() -> None:
    """Failed sign-ins are counted in Redis, which outlives the database between tests."""
    if not TEST_REDIS_URL:
        return
    redis = Redis.from_url(TEST_REDIS_URL)
    for key in redis.scan_iter("login:fail:*"):
        redis.delete(key)


def sign_in(client: TestClient, email: str, password: str = PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


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


def add_run(session_id: str, question: str) -> None:
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO runs (id, session_id, mode, question, status)"
            " VALUES (gen_random_uuid(), %s, 'agent', %s, 'complete')",
            (session_id, question),
        )


def test_past_conversations_are_listed_newest_first(client):
    client.cookies.clear()
    assert client.get("/api/sessions").json() == []  # a new browser has none
    first = client.post("/api/sessions").json()["id"]
    add_run(first, "What does the memo require?")
    add_run(first, "And the deadline?")
    empty = client.post("/api/sessions").json()["id"]  # no question yet: not listed
    second = client.post("/api/sessions").json()["id"]
    add_run(second, "Which functions make up the Core?")

    listed = client.get("/api/sessions").json()
    assert [c["id"] for c in listed] == [second, first]
    assert listed[1]["title"] == "What does the memo require?" and listed[1]["questions"] == 2
    assert empty not in {c["id"] for c in listed}

    client.cookies.clear()  # another browser sees none of them
    assert client.get("/api/sessions").json() == []


def test_a_signed_in_history_follows_the_account_to_another_browser(client):
    client.cookies.clear()
    r = client.post("/api/auth/register", json={"email": "ada@nyu.edu", "password": PASSWORD})
    assert r.status_code == 201
    ada = client.post("/api/sessions").json()["id"]
    add_run(ada, "When does the review board meet?")

    client.cookies.clear()  # a different browser, signed in to the same account
    r = client.post("/api/auth/login", json={"email": "ada@nyu.edu", "password": PASSWORD})
    assert r.status_code == 200
    assert [c["id"] for c in client.get("/api/sessions").json()] == [ada]
    assert client.get(f"/api/sessions/{ada}").status_code == 200


def test_your_own_upload_can_be_deleted_and_nothing_else(client):
    client.cookies.clear()
    shared = upload(client, "Shared policy text.")
    sign_up(client, "ada@nyu.edu")
    mine = upload(client, "Ada's own notes.")
    busy = upload(client, "Ada's second notes.")
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute("UPDATE documents SET status = 'ready' WHERE id = %s", (mine,))
        version = conn.execute("SELECT version FROM corpus_state").fetchone()[0]

    assert client.delete(f"/api/documents/{shared}").status_code == 404  # not hers to delete
    assert client.delete(f"/api/documents/{busy}").status_code == 409  # still being processed
    sign_up(client, "bo@nyu.edu")
    assert client.delete(f"/api/documents/{mine}").status_code == 404  # someone else's
    client.cookies.clear()
    assert client.delete(f"/api/documents/{mine}").status_code == 401  # signed out

    assert sign_in(client, "ada@nyu.edu").status_code == 200
    assert client.delete(f"/api/documents/{mine}").status_code == 204
    assert client.get(f"/api/documents/{mine}").status_code == 404
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        # Cached searches name the corpus version, so none that included it is read again.
        assert conn.execute("SELECT version FROM corpus_state").fetchone()[0] == version + 1
        assert (
            conn.execute("SELECT count(*) FROM chunks WHERE document_id = %s", (mine,)).fetchone()[
                0
            ]
            == 0
        )


def test_a_short_wrong_password_gets_the_usual_answer(client):
    sign_up(client, "ada@nyu.edu")
    client.cookies.clear()
    response = sign_in(client, "ada@nyu.edu", "short")
    assert response.status_code == 401
    assert response.json()["detail"] == "The email or the password is not right."


@needs_redis
def test_repeated_failed_sign_ins_lock_that_email_for_a_while(client):
    sign_up(client, "ada@nyu.edu")
    sign_up(client, "bo@nyu.edu")
    client.cookies.clear()
    for _ in range(5):
        assert sign_in(client, "ada@nyu.edu", "x" * 12).status_code == 401
    locked = sign_in(client, "ada@nyu.edu")  # the right password, but too late
    assert locked.status_code == 429
    assert 0 < int(locked.headers["Retry-After"]) <= 900
    assert sign_in(client, "bo@nyu.edu").status_code == 200  # other accounts are unaffected


@needs_redis
def test_a_successful_sign_in_clears_the_failed_count(client):
    sign_up(client, "ada@nyu.edu")
    client.cookies.clear()
    for _ in range(4):
        assert sign_in(client, "ada@nyu.edu", "x" * 12).status_code == 401
    assert sign_in(client, "ada@nyu.edu").status_code == 200
    for _ in range(4):
        assert sign_in(client, "ada@nyu.edu", "x" * 12).status_code == 401
    assert sign_in(client, "ada@nyu.edu").status_code == 200


def test_failed_sign_ins_are_counted_per_email_and_address():
    from app.api.auth import _failures_key

    one = _failures_key("Ada@NYU.edu ", "10.1.2.3")
    assert one == _failures_key("ada@nyu.edu", "10.1.2.3")  # the same email, any spelling
    assert one != _failures_key("ada@nyu.edu", "10.9.9.9")  # an attacker elsewhere counts apart


@needs_redis
async def test_attempts_sent_together_cannot_pass_the_limit_together(client):
    import asyncio

    from redis.asyncio import Redis as AsyncRedis

    from app.api.auth import LOGIN_LIMIT, _failures_key, take_attempt

    redis = AsyncRedis.from_url(TEST_REDIS_URL)
    key = _failures_key("race@nyu.edu", "10.0.0.7")
    waits = await asyncio.gather(*(take_attempt(redis, key) for _ in range(20)))
    assert sum(1 for w in waits if w == 0) == LOGIN_LIMIT  # only five may check a password
    await redis.delete(key)
    await redis.aclose()
