"""The metrics page matches the tables it is read from and carries no user text."""

import re
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from tests.conftest import TEST_DATABASE_URL, needs_db, needs_model, reset_schema

pytestmark = [needs_db, needs_model]

QUESTION = "What does the private handbook say about grant overhead?"


@pytest.fixture
def client():
    reset_schema()
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c


def scrape(client: TestClient) -> dict[str, float]:
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert QUESTION not in r.text
    samples = {}
    for line in r.text.splitlines():
        if line and not line.startswith("#"):
            name, value = line.rsplit(" ", 1)
            samples[name] = float(value)
    # Every sample belongs to a family declared with HELP and TYPE.
    families = set(re.findall(r"^# TYPE (\S+) ", r.text, re.M))
    for name in samples:
        base = name.split("{")[0]
        assert base in families or re.sub(r"_(bucket|sum|count)$", "", base) in families, name
    return samples


def test_metrics_match_the_run_and_model_call_tables(client):
    session = client.post("/api/sessions").json()["id"]
    runs = [
        ("agent", "complete", 3_000),
        ("agent", "complete", 12_000),
        ("baseline", "failed", 1_500),
        ("agent", "running", 0),
    ]
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        for i, (mode, status, ms) in enumerate(runs):
            waiting = status == "running"
            run_id = uuid.uuid4()
            # Each conversation holds one unresolved run, so the waiting one gets its own.
            sid = client.post("/api/sessions").json()["id"] if waiting else session
            conn.execute(
                """INSERT INTO runs (id, session_id, mode, question, status, exec_ms, finished_at,
                                     work, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, CASE WHEN %s THEN NULL ELSE now() END, %s,
                           now() - interval '5 seconds')""",
                (run_id, sid, mode, QUESTION, status, ms, waiting, "start" if waiting else None),
            )
            purpose = "support_check" if i == 2 else "agent_turn"
            conn.execute(
                """INSERT INTO llm_calls (run_id, purpose, model, input_tokens, output_tokens,
                                          cache_read_tokens, cost_usd, ms)
                   VALUES (%s, %s, 'claude-haiku-5-5', %s, %s, %s, %s, 900)""",
                (run_id, purpose, 1000 + i, 100, 50, 0.0012 + i / 1000),
            )
        ledger = dict(
            conn.execute(
                "SELECT purpose, sum(cost_usd)::float FROM llm_calls GROUP BY purpose"
            ).fetchall()
        )

    m = scrape(client)
    assert m['callslip_runs_finished_total{mode="agent",status="complete"}'] == 2
    assert m['callslip_runs_finished_total{mode="baseline",status="failed"}'] == 1
    assert m['callslip_runs_open{mode="agent",status="running"}'] == 1
    assert 'callslip_runs_finished_total{mode="agent",status="running"}' not in m

    # Agent runs took 3 s and 12 s on the workers; the running one is not finished.
    assert m['callslip_run_seconds_bucket{mode="agent",le="2"}'] == 0
    assert m['callslip_run_seconds_bucket{mode="agent",le="5"}'] == 1
    assert m['callslip_run_seconds_bucket{mode="agent",le="20"}'] == 2
    assert m['callslip_run_seconds_bucket{mode="agent",le="+Inf"}'] == 2
    assert m['callslip_run_seconds_sum{mode="agent"}'] == 15.0
    assert m['callslip_run_seconds_count{mode="baseline"}'] == 1

    assert m["callslip_runs_waiting"] == 1
    assert m["callslip_oldest_wait_seconds"] >= 5

    model = 'model="claude-haiku-5-5"'
    assert m[f'callslip_model_calls_total{{{model},purpose="agent_turn"}}'] == 3
    assert (
        m[f'callslip_model_tokens_total{{{model},purpose="agent_turn",kind="input"}}']
        == 1000 + 1001 + 1003
    )
    support = f'{model},purpose="support_check"'
    assert m[f'callslip_model_tokens_total{{{support},kind="cache_read"}}'] == 50
    for purpose, cost in ledger.items():
        assert m[f'callslip_model_cost_usd_total{{{model},purpose="{purpose}"}}'] == pytest.approx(
            cost
        )


def test_metrics_are_not_under_the_proxied_api_path(client):
    # The web server and the public route forward only /api, which keeps this page internal.
    assert client.get("/api/metrics").status_code == 404
