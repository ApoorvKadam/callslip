"""Session isolation, the one-unresolved-run rule and the event stream, through the real app.

No model is called here: runs are written straight to the database where a test needs one.
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from app.api.sessions import COOKIE
from tests.conftest import (
    TEST_DATABASE_URL,
    TEST_REDIS_URL,
    needs_db,
    needs_model,
    needs_redis,
    reset_schema,
)

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


def test_a_reply_cannot_borrow_another_replys_key(client):
    session = new_browser(client)
    client.app.state.llm = NoModel()
    run = insert_run(session, "needs_clarification")
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "UPDATE runs SET mode = 'agent', pending_tool_use_id = 'toolu_1' WHERE id = %s", (run,)
        )
    url = f"/api/sessions/{session}/runs/{run}/resume"
    first = {"tool_use_id": "toolu_1", "idempotency_key": "key-0003", "reply": "alpha\nbeta"}
    assert client.post(url, json=first).status_code == 202
    # Joined with a newline, these two would read the same; they must not.
    other = {**first, "tool_use_id": "toolu_1\nalpha", "reply": "beta"}
    assert client.post(url, json=other).status_code == 409


def test_compare_asks_both_ways_in_one_new_conversation(client):
    client.app.state.llm = NoModel()
    session = new_browser(client)
    r = client.post(f"/api/sessions/{session}/compare", json={"question": "What does the RMF say?"})
    assert r.status_code == 202
    runs = r.json()
    assert sorted(run["mode"] for run in runs) == ["agent", "baseline"]
    assert runs[0]["compare_id"] and runs[0]["compare_id"] == runs[1]["compare_id"]
    # The comparison holds that one question: no follow-up, no second comparison.
    more = client.post(f"/api/sessions/{session}/runs", json={"question": "And then?"})
    assert more.status_code == 409
    again = client.post(f"/api/sessions/{session}/compare", json={"question": "Again?"})
    assert again.status_code == 409
    listed = next(s for s in client.get("/api/sessions").json() if s["id"] == session)
    assert (listed["compare"], listed["questions"]) == (True, 2)


def test_compare_needs_an_empty_conversation(client):
    client.app.state.llm = NoModel()
    session = new_browser(client)
    insert_run(session, "complete")
    r = client.post(f"/api/sessions/{session}/compare", json={"question": "Q?"})
    assert r.status_code == 409


def test_another_browser_cannot_compare_in_a_conversation(client):
    client.app.state.llm = NoModel()
    session = new_browser(client)
    new_browser(client)
    r = client.post(f"/api/sessions/{session}/compare", json={"question": "Q?"})
    assert r.status_code == 404


@needs_redis
def test_questions_from_one_address_are_limited(client, monkeypatch):
    from redis import Redis

    client.app.state.llm = NoModel()
    monkeypatch.setattr(client.app.state.settings, "ask_limit", 2)
    redis = Redis.from_url(TEST_REDIS_URL)
    for key in redis.scan_iter("ask:addr:*"):
        redis.delete(key)
    for _ in range(2):
        session = new_browser(client)
        assert (
            client.post(f"/api/sessions/{session}/runs", json={"question": "Q?"}).status_code == 202
        )
    session = new_browser(client)
    refused = client.post(f"/api/sessions/{session}/compare", json={"question": "Q?"})
    assert refused.status_code == 429
    assert 0 < int(refused.headers["Retry-After"]) <= 600
    assert "Too many questions" in refused.json()["detail"]
    for key in redis.scan_iter("ask:addr:*"):
        redis.delete(key)


def test_a_run_shows_its_clarifying_question_and_the_reply(client):
    session = new_browser(client)
    run = insert_run(
        session,
        "complete",
        [
            ("clarification", {"question": "Which memo?", "options": ["OMB M-24-10"]}),
            ("clarification_answered", {"reply": "OMB M-24-10"}),
        ],
    )
    shown = client.get(f"/api/sessions/{session}").json()["runs"]
    assert (shown[0]["asked"], shown[0]["replied"]) == ("Which memo?", "OMB M-24-10")
    single = client.get(f"/api/runs/{run}").json()
    assert (single["asked"], single["replied"]) == ("Which memo?", "OMB M-24-10")
