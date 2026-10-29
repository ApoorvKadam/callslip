"""Operational metrics in the Prometheus text format, read from the database on each scrape.

`/metrics` sits outside `/api`, so the web server and the public route never forward it. With
Compose, read it inside the API container. On Kubernetes, the API's network policy admits only
the ingress controller, so a Prometheus needs its own allow rule first. It reports counts, times,
tokens and cost. Nothing a user wrote (questions,
answers, document titles) appears in it.

The numbers come from the tables the app already keeps: `runs`, `llm_calls` and `documents`.
Runs and model calls are never deleted, and a run's status, time and counts are written once,
together, when it finishes. So totals over finished runs and over model calls only grow and are
counters; runs still open move between statuses and are a gauge.
"""

from typing import Annotated, LiteralString

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from psycopg_pool import AsyncConnectionPool

from app.api.deps import get_pool

router = APIRouter(tags=["metrics"])

# Upper bounds, in seconds, for the run time histogram. Answers usually take 4 to 10 seconds.
RUN_BUCKETS = (2, 5, 10, 20, 30, 60, 90)

QUERIES: dict[str, LiteralString] = {
    "runs": """
        SELECT mode, status, finished_at IS NOT NULL, count(*)
          FROM runs GROUP BY 1, 2, 3 ORDER BY 1, 2
    """,
    # Time the run workers spent executing finished runs (model calls, tools, the quote check);
    # a clarification's wait for the user is not in it.
    "run_seconds": """
        SELECT mode,
               array_agg(n ORDER BY le) AS buckets,
               max(total_count) AS count,
               max(total_sum) AS sum
          FROM (SELECT mode, le,
                       count(*) FILTER (WHERE exec_ms <= le * 1000) AS n,
                       count(*) AS total_count,
                       sum(exec_ms) / 1000.0 AS total_sum
                  FROM runs CROSS JOIN unnest(%s::int[]) AS le
                 WHERE finished_at IS NOT NULL
                 GROUP BY mode, le) AS b
         GROUP BY mode ORDER BY mode
    """,
    # Questions recorded but not yet picked up by a run worker.
    "waiting": """
        SELECT count(*), coalesce(extract(epoch FROM now() - min(created_at)), 0)
          FROM runs WHERE status = 'running' AND work IS NOT NULL
    """,
    "model": """
        SELECT model, purpose, count(*), sum(input_tokens), sum(output_tokens),
               sum(cache_read_tokens), sum(cache_creation_tokens), sum(cost_usd)
          FROM llm_calls GROUP BY 1, 2 ORDER BY 1, 2
    """,
    "documents": "SELECT status, count(*) FROM documents GROUP BY 1 ORDER BY 1",
}


def _labels(**labels: object) -> str:
    # Label values here are fixed words from the app (modes, statuses, model names), but escape
    # them anyway so a model name can never break the format.
    parts = []
    for key, value in labels.items():
        value = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        parts.append(f'{key}="{value}"')
    return "{" + ",".join(parts) + "}"


def render(rows: dict[str, list[tuple]]) -> str:
    out: list[str] = []

    def family(name: str, kind: str, help_: str) -> None:
        out.append(f"# HELP {name} {help_}")
        out.append(f"# TYPE {name} {kind}")

    family("callslip_runs_finished_total", "counter", "Finished runs, by mode and outcome.")
    for mode, status, finished, n in rows["runs"]:
        if finished:
            out.append(f"callslip_runs_finished_total{_labels(mode=mode, status=status)} {n}")
    family("callslip_runs_open", "gauge", "Runs running or waiting for a clarification.")
    for mode, status, finished, n in rows["runs"]:
        if not finished:
            out.append(f"callslip_runs_open{_labels(mode=mode, status=status)} {n}")

    family("callslip_run_seconds", "histogram", "Worker time of finished runs, by mode.")
    for mode, buckets, count, total in rows["run_seconds"]:
        for le, n in zip(RUN_BUCKETS, buckets, strict=True):
            out.append(f"callslip_run_seconds_bucket{_labels(mode=mode, le=le)} {n}")
        out.append(f"callslip_run_seconds_bucket{_labels(mode=mode, le='+Inf')} {count}")
        out.append(f"callslip_run_seconds_sum{_labels(mode=mode)} {float(total):.3f}")
        out.append(f"callslip_run_seconds_count{_labels(mode=mode)} {count}")

    waiting, oldest = rows["waiting"][0]
    family("callslip_runs_waiting", "gauge", "Questions no run worker has started yet.")
    out.append(f"callslip_runs_waiting {waiting}")
    family("callslip_oldest_wait_seconds", "gauge", "Wait of the oldest question not yet started.")
    out.append(f"callslip_oldest_wait_seconds {float(oldest):.3f}")

    family("callslip_model_calls_total", "counter", "Model calls, by model and purpose.")
    for model, purpose, n, *_ in rows["model"]:
        out.append(f"callslip_model_calls_total{_labels(model=model, purpose=purpose)} {n}")
    family("callslip_model_tokens_total", "counter", "Model tokens, by model and kind.")
    for model, purpose, _, inp, outp, read, write, _ in rows["model"]:
        kinds = {"input": inp, "output": outp, "cache_read": read, "cache_write": write}
        for kind, n in kinds.items():
            labels = _labels(model=model, purpose=purpose, kind=kind)
            out.append(f"callslip_model_tokens_total{labels} {n}")
    family("callslip_model_cost_usd_total", "counter", "Estimated model cost in US dollars.")
    for model, purpose, *_, cost in rows["model"]:
        out.append(f"callslip_model_cost_usd_total{_labels(model=model, purpose=purpose)} {cost}")

    family("callslip_documents", "gauge", "Documents, by ingestion status.")
    for status, n in rows["documents"]:
        out.append(f"callslip_documents{_labels(status=status)} {n}")

    return "\n".join(out) + "\n"


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics(pool: Annotated[AsyncConnectionPool, Depends(get_pool)]) -> PlainTextResponse:
    rows: dict[str, list[tuple]] = {}
    async with pool.connection() as conn:
        for name, sql in QUERIES.items():
            params = (list(RUN_BUCKETS),) if name == "run_seconds" else None
            rows[name] = await (await conn.execute(sql, params)).fetchall()
    return PlainTextResponse(render(rows), media_type="text/plain; version=0.0.4")
