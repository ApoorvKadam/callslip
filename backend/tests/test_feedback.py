"""Rating answers and the viewer's own insights, through the real app and a real PostgreSQL.

No model is called: finished runs are written straight to the database.
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from tests.conftest import TEST_DATABASE_URL, needs_db, needs_model, reset_schema

pytestmark = [needs_db, needs_model]

ANSWER = {"text": "x", "segments": [], "citations": [{}, {}], "citations_verified": 1}


@pytest.fixture
def client():
    reset_schema()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def new_browser(client: TestClient) -> str:
    client.cookies.clear()
    return client.post("/api/sessions").json()["id"]


def insert_run(
    session_id: str, status: str = "complete", finished: bool = True, exec_ms: int = 4000
) -> str:
    run_id = str(uuid.uuid4())
    answered = finished and status != "failed"
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO runs (id, session_id, mode, question, status, answer, exec_ms,"
            " finished_at) VALUES (%s, %s, 'agent', 'q', %s, %s, %s,"
            " CASE WHEN %s THEN now() END)",
            (run_id, session_id, status, Jsonb(ANSWER) if answered else None, exec_ms, finished),
        )
        conn.execute(
            "INSERT INTO llm_calls (run_id, purpose, model, input_tokens, output_tokens,"
            " cost_usd, ms) VALUES (%s, 'agent', 'm', 10, 10, 0.002, 1)",
            (run_id,),
        )
    return run_id


def test_a_finished_answer_is_rated_and_the_rating_replaces_the_last(client):
    session = new_browser(client)
    run = insert_run(session)
    url = f"/api/runs/{run}/feedback"

    no = client.put(url, json={"helpful": False, "note": "  Missed the 2024 memo.  "})
    assert no.json() == {"helpful": False, "note": "Missed the 2024 memo."}
    shown = client.get(f"/api/sessions/{session}").json()["runs"][0]["feedback"]
    assert shown == {"helpful": False, "note": "Missed the 2024 memo."}

    # "Useful" keeps no note, even one sent along.
    yes = client.put(url, json={"helpful": True, "note": "ignored"})
    assert yes.json() == {"helpful": True, "note": None}
    assert client.get(f"/api/runs/{run}").json()["feedback"] == {"helpful": True, "note": None}


def test_only_finished_answers_can_be_rated(client):
    session = new_browser(client)
    running = insert_run(session, status="running", finished=False)
    r = client.put(f"/api/runs/{running}/feedback", json={"helpful": True})
    assert r.status_code == 409


def test_another_browser_cannot_rate_or_see_a_rating(client):
    session = new_browser(client)
    run = insert_run(session)
    client.put(f"/api/runs/{run}/feedback", json={"helpful": False, "note": "private"})
    new_browser(client)
    assert client.put(f"/api/runs/{run}/feedback", json={"helpful": True}).status_code == 404
    assert client.get(f"/api/runs/{run}").status_code == 404


def test_a_note_longer_than_500_characters_is_refused(client):
    session = new_browser(client)
    run = insert_run(session)
    r = client.put(f"/api/runs/{run}/feedback", json={"helpful": False, "note": "x" * 501})
    assert r.status_code == 422


def test_insights_count_only_the_viewers_own_questions(client):
    mine = new_browser(client)
    rated = insert_run(mine)
    insert_run(mine, status="incomplete")
    insert_run(mine, status="running", finished=False)
    # Failed runs have no answer, so their time stays out of the answers' median.
    for _ in range(3):
        insert_run(mine, status="failed", exec_ms=90000)
    client.put(f"/api/runs/{rated}/feedback", json={"helpful": False})
    own = client.get("/api/insights").json()

    new_browser(client)
    insert_run(new_browser(client))
    other = client.get("/api/insights").json()

    assert own["runs"] == 6 and own["complete"] == 1 and own["incomplete"] == 1
    assert own["failed"] == 3 and own["open"] == 1 and own["rateable"] == 2
    assert (own["useful"], own["not_useful"]) == (0, 1)
    assert (own["citations"], own["citations_verified"]) == (4, 2)
    assert own["median_ms"] == 4000 and round(own["cost_usd"], 3) == 0.012
    assert other["runs"] == 1 and other["not_useful"] == 0


def test_a_visitor_without_a_conversation_sees_zeros(client):
    client.cookies.clear()
    r = client.get("/api/insights")
    assert r.status_code == 200 and r.json()["runs"] == 0
