# Deployment runbook

Everything runs with Docker Compose: `frontend` (nginx + React), `api` (FastAPI), `worker` (ingestion), `postgres` (PostgreSQL 17 + pgvector) and `redis` (cache). Commands below are run from the repository root. Captured output from a real run is in [Evidence](#evidence).

## Requirements

- Docker with Compose v2 (tested with Docker 29.9, Compose 5.6), about 3 GB of free memory. Each container has a memory limit (`mem_limit` in `docker-compose.yml`): api 1 GiB, worker 1 GiB, postgres 512 MiB, redis 128 MiB, frontend 64 MiB.
- An Anthropic API key for answers. Without it, documents and search work and asking a question returns 503.

## Configuration and secrets

| Variable | Where | Default | Notes |
|---|---|---|---|
| `POSTGRES_PASSWORD` | `.env` | required | any long random string |
| `ANTHROPIC_API_KEY` | `.env` | empty | secret; never committed, never logged; CI has none |
| `POSTGRES_USER`, `POSTGRES_DB` | `.env` | `rag` | |
| `WEB_PORT` | `.env` | `8080` | the only published port |
| `IMAGE_TAG` | shell | `dev` | image tag; `scripts/deploy.sh` sets it to the commit SHA |
| `ALLOW_FAULT_INJECTION` | shell or `.env` | `false` | evaluation only: lets a request make a tool fail |
| `LOG_LEVEL` | `.env` | `INFO` | |

Application settings with their defaults are in `backend/app/config.py` (model `claude-sonnet-5-5`, effort `medium`, `top_k` 8, run deadline 90 s, 10 model turns, 9 tool calls, 8 s tool timeout). Any of them can be set in `.env` under the same name in capitals, for example `RUN_DEADLINE_S=60`; Compose passes `.env` to the api and worker. Recreate the service to apply it: `docker compose up -d --wait api`.

`.env` is git-ignored; `.env.example` is the template. Secrets reach containers only as environment variables from `.env`; PostgreSQL and Redis are not published to the host.

## Deploy

```bash
cp .env.example .env              # first time: set POSTGRES_PASSWORD and ANTHROPIC_API_KEY
scripts/deploy.sh                 # build images tagged with the commit SHA, start, verify
python3 scripts/load_corpus.py    # load the 14 corpus PDFs (safe to run again)
```

`deploy.sh` runs `docker compose build` and `docker compose up -d --wait` with `IMAGE_TAG=<short SHA>`, waits for every health check, then runs `scripts/verify.sh`. Only after verification passes is the tag recorded in `.deploy/current`, and the one it replaces in `.deploy/previous`. A failed verification leaves both unchanged and prints the last verified tag to roll back to.

Plain Compose works too: `docker compose up -d --build --wait`.

## Verify

```bash
scripts/verify.sh                 # container health, /api/health, /api/ready, upload, ingest, search
python3 scripts/ask.py "What are the four functions of the NIST AI RMF Core?"   # needs the key
```

Health checks: `api` calls `/api/health`; `worker` checks that its heartbeat file is fresh (it is touched every 10 s, also during long documents); `postgres` runs `pg_isready`; `redis` runs `redis-cli ping`; `frontend` fetches `/healthz`. `/api/ready` reports each dependency: PostgreSQL down gives 503; Redis down gives 200 with `"status": "degraded"`.

## Update

```bash
git pull
scripts/deploy.sh                 # new images tagged with the new SHA; migrations run at startup
```

Migrations are numbered SQL files in `backend/app/migrations/`, applied once each at startup under a PostgreSQL advisory lock (the api and worker never migrate at the same time). They only add tables and columns, so the previous release still runs on the new schema.

## Roll back

```bash
scripts/rollback.sh               # back to the previous tag, no rebuild, then verify
scripts/rollback.sh 1a2b3c4       # or any tag still present locally (docker images agentic-rag-*)
```

Data is not rolled back: documents, runs and the ledger stay. Because migrations are additive, an older release ignores tables and columns it does not know.

## Persistence

- All state is in PostgreSQL on the named volume `agentic-rag_pgdata`: documents and their raw PDF bytes, pages, passages with vectors, sessions, runs, the exact model conversations, trace events and the model-call ledger.
- `docker compose down` and `up` (or `restart`) keep it; only `docker compose down -v` deletes it. After `deploy.sh`, start with the deployed tag: `IMAGE_TAG=$(cat .deploy/current) docker compose up -d --wait`; a plain `docker compose up` uses the `dev` tag.
- Redis holds only cache entries, with no persistence (`--save "" --appendonly no`); losing it costs only cache misses.
- Backup: `docker compose exec -T postgres pg_dump -U rag rag | gzip > backup.sql.gz`. Restore into an empty database: `gunzip -c backup.sql.gz | docker compose exec -T postgres psql -U rag rag`. Then give the restored database a new cache epoch, so nothing cached before the restore can be read again: `docker compose exec -T postgres psql -U rag rag -c "UPDATE corpus_state SET epoch = gen_random_uuid()"`. (A restore brings back the old epoch and version, and versions published after the backup would otherwise be reused.)

## Redis outage

```bash
docker compose stop redis
curl -s localhost:8080/api/ready          # {"status":"degraded","checks":{"database":"up","redis":"down"}}
python3 scripts/ask.py "..."              # still answers; the trace shows cache: unavailable
docker compose start redis
```

The first failed Redis call costs at most one 0.25 s timeout; Redis is then skipped for 30 s. CI runs this check on every pull request.

## Logging

Every service logs to stdout. Application logs from the API and worker are one JSON object per line (`ts`, `level`, `logger`, `msg` and fields such as `run_id`, `document_id`); uvicorn's access lines stay plain text. Examples:

```bash
docker compose logs -f api worker
# warnings and errors only, from the JSON lines
docker compose logs api worker --no-log-prefix | grep '^{' | python3 -c "import json,sys; [print(e['ts'], e['level'], e['msg']) for e in map(json.loads, sys.stdin) if e['level'] != 'INFO']"
```

A failed run shows the user a plain cause and a short reference; the full exception is in the API log under the same reference. Per-run detail (every tool call, model turn, tokens and cost) is in PostgreSQL and in the UI trace; total model spend: `docker compose exec postgres psql -U rag rag -c "select count(*), sum(cost_usd) from llm_calls"`.

## Scaling

| Part | Now | Next step |
|---|---|---|
| Frontend | one nginx | any number of replicas behind a load balancer |
| Worker | one process, one job at a time | `docker compose up -d --scale worker=3`: jobs are claimed with `FOR UPDATE SKIP LOCKED` and leases, so workers never take the same document |
| API | one instance; runs execute as background tasks in it | move runs to a queue consumed by run workers and live events to Redis pub/sub; then scale replicas (startup's cleanup of interrupted runs assumes one instance today) |
| PostgreSQL | exact vector search | HNSW index past about 100k passages (and check filtered recall); read replicas; raw PDFs to object storage |
| Model API | SDK retries inside each call's time budget | a per-tenant concurrency limit and a shared rate limiter in Redis |

On Kubernetes or OpenShift the same images become three Deployments (frontend, api, worker) with the existing liveness and readiness endpoints, plus managed PostgreSQL and Redis.

## Evidence

Captured on 2026-10-27 (ET) on the development machine (WSL 2, Docker 29.9, Compose 5.6), against a database that already held the 14 corpus documents. CI runs the same smoke, restart and Redis checks on every pull request.

### First deploy: commit `5d4f6e6`, 22:57, 42 s

PostgreSQL and Redis were already running and were left alone; Compose recreates only the containers whose image changed.

```text
$ scripts/deploy.sh
building images agentic-rag-*:5d4f6e6
starting 5d4f6e6
SERVICE    STATUS
api        Up 23 seconds (healthy)
frontend   Up 11 seconds (healthy)
postgres   Up 56 minutes (healthy)
redis      Up 5 minutes (healthy)
worker     Up 23 seconds (healthy)
health: 200 {'status': 'ok'}
ready: 200 {'status': 'ok', 'checks': {'database': 'up', 'redis': 'up'}}
upload: 202 document 30 queued
ingest: ready after 6.0s, pages=1, passages=1, error=None
search: 200, 1 hits, cache=miss, ms=24
  page 1  score 0.0328  Smoke test document, uploaded by scripts/smoke_test.py.
verify: ok
deployed 5d4f6e6 (previous: none)
```

### Update: commit `fd1da89`, 23:08, 31 s

The docs commit `c1e797b` had been deployed in between, so it is the previous tag.

```text
$ git pull && scripts/deploy.sh
building images agentic-rag-*:fd1da89
starting fd1da89
SERVICE    STATUS
api        Up 16 seconds (healthy)
frontend   Up 10 seconds (healthy)
postgres   Up 6 minutes (healthy)
redis      Up About a minute (healthy)
worker     Up 17 seconds (healthy)
health: 200 {'status': 'ok'}
ready: 200 {'status': 'ok', 'checks': {'database': 'up', 'redis': 'up'}}
upload: already present as document 30
ingest: ready after 0.0s, pages=1, passages=1, error=None
search: 200, 1 hits, cache=miss, ms=29
  page 1  score 0.0328  Smoke test document, uploaded by scripts/smoke_test.py.
verify: ok
deployed fd1da89 (previous: c1e797b)
```

A second run of the smoke test finds its document already present (409) and reuses it, so verifying never adds documents.

### Roll back: 23:09:37 to 23:09:57, no rebuild

```text
$ scripts/rollback.sh
rolling back to c1e797b
SERVICE    STATUS
api        Up 16 seconds (healthy)
frontend   Up 10 seconds (healthy)
postgres   Up 7 minutes (healthy)
redis      Up 44 seconds (healthy)
worker     Up 16 seconds (healthy)
health: 200 {'status': 'ok'}
ready: 200 {'status': 'ok', 'checks': {'database': 'up', 'redis': 'up'}}
upload: already present as document 30
ingest: ready after 0.0s, pages=1, passages=1, error=None
search: 200, 1 hits, cache=miss, ms=24
  page 1  score 0.0328  Smoke test document, uploaded by scripts/smoke_test.py.
verify: ok
running c1e797b
```

Then forward again to the newest tag:

```text
$ scripts/rollback.sh fd1da89
rolling back to fd1da89
verify: ok
running fd1da89
```

### A deploy that fails verification

Simulated by pointing the check at a closed port; the recorded tags stay as they were:

```text
$ BASE_URL=http://localhost:1 scripts/deploy.sh
...
urllib.error.URLError: <urlopen error [Errno 111] Connection refused>
verify failed for 4058c15; last verified: fd1da89 (scripts/rollback.sh fd1da89)
$ cat .deploy/current .deploy/previous
fd1da89
c1e797b
```

### Full restart keeps all data

```text
$ docker compose down && IMAGE_TAG=$(cat .deploy/current) docker compose up -d --wait
documents before: 15, after: 15; runs before: 97, after: 97
```

The 15 documents are the 14 corpus PDFs and the smoke test document.

### Redis outage

```text
$ docker compose stop redis
$ curl -s localhost:8080/api/ready
{"status":"degraded","checks":{"database":"up","redis":"down"}}
$ python3 scripts/ask.py "What are the four functions of the NIST AI RMF Core?"
status: complete
  tool search_documents {"query": "AI RMF Core four functions Govern Map Measure Manage"} -> ok, 8 passages, cache unavailable, 310 ms
[1] NIST AI 100-1: Artificial Intelligence Risk Management Framework (AI RMF 1.0), January 2023, page 25 (doc 1, page 25) verified: "NIST AI 100-1 AI  ...
totals: 5733 ms, 2 model calls, 1 tool calls, $0.0286
$ docker compose start redis && curl -s localhost:8080/api/ready
{"status":"ok","checks":{"database":"up","redis":"up"}}
```

The only log line in the API during the outage was the expected warning:

```text
2026-10-28T03:09:03.173+00:00 WARNING app.cache redis unavailable; continuing without cache
```

An earlier run of the same check also logged `Future exception was never retrieved` at ERROR. It came from uvloop (issue 437 in its tracker), so the API now runs on the standard asyncio loop.
