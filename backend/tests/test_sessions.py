"""Session isolation, the one-unresolved-run rule and the event stream, through the real app.

No model is called here: runs are written straight to the database where a test needs one.
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from app.api.sessions import COOKIE
from tests.conftest import TEST_DATABASE_URL, needs_db, needs_model, reset_schema

pytestmark = [needs_db, needs_model]


@pytest.fixture
def client():
    reset_schema()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def new_browser(client: TestClient) -> str:
    """Forget the current cookie, create a session as a fresh browser, return its id."""
    client.cookies.clear()
    r = client.post("/api/sessions")
    assert r.status_code == 201
    return r.json()["id"]


def insert_run(session_id: str, status: str, events: list[tuple[str, dict]] = ()) -> str:
    run_id = str(uuid.uuid4())
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO runs (id, session_id, mode, question, status) VALUES (%s, %s, %s, %s, %s)",
            (run_id, session_id, "baseline", "q", status),
        )
        for seq, (type_, data) in enumerate(events, start=1):
            conn.execute(
                "INSERT INTO run_events (run_id, seq, type, data) VALUES (%s, %s, %s, %s)",
                (run_id, seq, type_, Jsonb(data)),
            )
    return run_id


def test_creating_a_session_sets_an_httponly_cookie(client):
    client.cookies.clear()
    r = client.post("/api/sessions")
    cookie = r.headers["set-cookie"]
    assert cookie.startswith(f"{COOKIE}=")
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/api" in cookie


def test_a_session_is_private_to_its_browser(client):
    mine = new_browser(client)
    my_cookie = client.cookies.get(COOKIE)
    assert client.get(f"/api/sessions/{mine}").status_code == 200

    new_browser(client)  # another browser
    assert client.get(f"/api/sessions/{mine}").status_code == 404

    client.cookies.clear()  # no cookie at all
    assert client.get(f"/api/sessions/{mine}").status_code == 404

    client.cookies.set(COOKIE, my_cookie, path="/api")
    assert client.get(f"/api/sessions/{mine}").status_code == 200


def test_runs_and_their_events_are_private_too(client):
    session = new_browser(client)
    run = insert_run(session, "complete", [("run_started", {"question": "q"})])
    assert client.get(f"/api/runs/{run}").status_code == 200
    new_browser(client)
    assert client.get(f"/api/runs/{run}").status_code == 404
    assert client.get(f"/api/runs/{run}/events").status_code == 404


def test_a_second_question_waits_for_the_unresolved_one(client):
    session = new_browser(client)
    insert_run(session, "needs_clarification")
    r = client.post(f"/api/sessions/{session}/runs", json={"question": "Another question?"})
    # 409 with a key configured; 503 when the environment running the tests has none.
    assert r.status_code in (409, 503)


def test_blank_questions_are_rejected(client):
    session = new_browser(client)
    r = client.post(f"/api/sessions/{session}/runs", json={"question": "   "})
    assert r.status_code == 422


def test_event_stream_replays_with_ids_and_ends_when_the_run_is_over(client):
    session = new_browser(client)
    run = insert_run(
        session,
        "complete",
        [("run_started", {"question": "q"}), ("answer", {"text": "a"}), ("run_finished", {})],
    )
    body = client.get(f"/api/runs/{run}/events").text
    assert "id: 1\nevent: run_started" in body
    assert "id: 3\nevent: run_finished" in body
    assert body.rstrip().endswith('event: end\ndata: {"status": "complete"}')

    # Reconnecting with Last-Event-ID only sends what was missed.
    resumed = client.get(f"/api/runs/{run}/events", headers={"Last-Event-ID": "2"}).text
    assert "id: 1\n" not in resumed and "id: 3\nevent: run_finished" in resumed


class NoModel:
    """Stands in for the model client so resume is allowed; the resumed run stops at once."""

    async def create(self, **_):
        raise TimeoutError


def test_a_reply_is_accepted_once_per_key(client):
    session = new_browser(client)
    client.app.state.llm = NoModel()
    run = insert_run(session, "needs_clarification")
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "UPDATE runs SET mode = 'agent', pending_tool_use_id = 'toolu_1' WHERE id = %s", (run,)
        )
    url = f"/api/sessions/{session}/runs/{run}/resume"
    body = {"tool_use_id": "toolu_1", "idempotency_key": "key-0001", "reply": "OMB M-25-21"}
    assert client.post(url, json=body).status_code == 202
    assert client.post(url, json=body).status_code == 202  # the same reply, sent again
    assert client.post(url, json={**body, "reply": "OMB M-24-10"}).status_code == 409
    assert client.post(url, json={**body, "idempotency_key": "key-0002"}).status_code == 409
