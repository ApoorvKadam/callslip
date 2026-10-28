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

Application settings with their defaults are in `backend/app/config.py` (model `claude-haiku-5-5`, effort `medium`, `top_k` 8, run deadline 90 s, 10 model turns, 9 tool calls, 8 s tool timeout). Any of them can be set in `.env` under the same name in capitals, for example `RUN_DEADLINE_S=60`; Compose passes `.env` to the api and worker. Recreate the service to apply it: `docker compose up -d --wait api`.

`.env` is git-ignored; `.env.example` is the template. Secrets reach containers only as environment variables from `.env`; PostgreSQL and Redis are not published to the host.

## Deploy

```bash
cp .env.example .env              # first time: set POSTGRES_PASSWORD and ANTHROPIC_API_KEY
scripts/deploy.sh                 # build images tagged with the commit SHA, start, verify
python3 scripts/load_corpus.py    # load the 14 corpus PDFs (safe to run again)
```

`deploy.sh` refuses to build when `backend/`, `frontend/` or `docker-compose.yml` has uncommitted changes, because the image tag must name the code inside it. It then runs `docker compose build` and `docker compose up -d --wait` with `IMAGE_TAG=<short SHA>`, waits for every health check, and runs `scripts/verify.sh`. Only after verification passes is the tag recorded in `.deploy/current`, and the one it replaces in `.deploy/previous`. A failed verification leaves both unchanged and prints the last verified tag to roll back to.

Plain Compose works too: `docker compose up -d --build --wait`.

## Verify

```bash
scripts/verify.sh                 # every service healthy, /api/health, /api/ready, upload, ingest, search
python3 scripts/ask.py "What are the four functions of the NIST AI RMF Core?"   # needs the key
```

`verify.sh` fails if any service is missing, stopped or not healthy, and it tests the port that Compose publishes (`WEB_PORT`) unless `BASE_URL` is set.

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
scripts/rollback.sh 1a2b3c4       # or any tag still present locally (docker images 'callslip-*')
```

Data is not rolled back: documents, runs and the ledger stay. Because migrations are additive, an older release ignores tables and columns it does not know.

## Persistence

- All state is in PostgreSQL on the named volume `callslip_pgdata`: documents and their raw PDF bytes, pages, passages with vectors, sessions, runs, the exact model conversations, trace events and the model-call ledger.
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
| API | stateless: it queues runs and streams their events | any number of replicas behind the load balancer |
| Run workers | `runner`, up to 4 runs at a time each | `docker compose up -d --scale runner=3`: runs are claimed with `FOR UPDATE SKIP LOCKED` and leases, and a run whose worker died is closed by the others |
| PostgreSQL | exact vector search | HNSW index past about 100k passages (and check filtered recall); read replicas; raw PDFs to object storage |
| Model API | SDK retries inside each call's time budget | a per-tenant concurrency limit and a shared rate limiter in Redis |

On Kubernetes or OpenShift the same images become three Deployments (frontend, api, worker) with the existing liveness and readiness endpoints, plus managed PostgreSQL and Redis.

## Evidence

Captured on 2026-10-28 (ET) on the development machine (WSL 2, Docker 29.9, Compose 5.6), right after the rename to Callslip. The old project's data volume had been copied into `callslip_pgdata`, so the database already held the 14 corpus documents. CI runs the same smoke, restart and Redis checks on every pull request.

### First deploy: commit `48858cb`, 02:02, 99 s

The first build under the new image names; the frontend image was rebuilt because its package name changed.

```text
$ scripts/deploy.sh
building images callslip-*:48858cb
...
SERVICE    STATUS
api        Up 16 seconds (healthy)
frontend   Up 10 seconds (healthy)
postgres   Up 22 seconds (healthy)
redis      Up 22 seconds (healthy)
worker     Up 16 seconds (healthy)
health: 200 {'status': 'ok'}
ready: 200 {'status': 'ok', 'checks': {'database': 'up', 'redis': 'up'}}
upload: already present as document 30
ingest: ready after 0.0s, pages=1, passages=1, error=None
search: 200, 1 hits, cache=miss, ms=20
  page 1  score 0.0328  Smoke test document, uploaded by scripts/smoke_test.py.
verify: ok
deployed 48858cb (previous: none)
```

The smoke test finds its document already present (409) and reuses it, so verifying never adds documents.

### Update: commit `cccefb1`, 02:04, 24 s

PostgreSQL and Redis were left alone; Compose recreates only the containers whose image changed.

```text
$ git pull && scripts/deploy.sh
building images callslip-*:cccefb1
...
SERVICE    STATUS
api        Up 16 seconds (healthy)
frontend   Up 10 seconds (healthy)
postgres   Up About a minute (healthy)
redis      Up About a minute (healthy)
worker     Up 16 seconds (healthy)
health: 200 {'status': 'ok'}
ready: 200 {'status': 'ok', 'checks': {'database': 'up', 'redis': 'up'}}
upload: already present as document 30
ingest: ready after 0.0s, pages=1, passages=1, error=None
search: 200, 1 hits, cache=hit, ms=3
  page 1  score 0.0328  Smoke test document, uploaded by scripts/smoke_test.py.
verify: ok
deployed cccefb1 (previous: 48858cb)
```

### Roll back: 02:04:39 to 02:04:59, no rebuild

```text
$ scripts/rollback.sh
rolling back to 48858cb
SERVICE    STATUS
api        Up 16 seconds (healthy)
frontend   Up 10 seconds (healthy)
postgres   Up About a minute (healthy)
redis      Up About a minute (healthy)
worker     Up 16 seconds (healthy)
health: 200 {'status': 'ok'}
ready: 200 {'status': 'ok', 'checks': {'database': 'up', 'redis': 'up'}}
upload: already present as document 30
ingest: ready after 0.0s, pages=1, passages=1, error=None
search: 200, 1 hits, cache=hit, ms=2
  page 1  score 0.0328  Smoke test document, uploaded by scripts/smoke_test.py.
verify: ok
running 48858cb
```

### A deploy that fails verification

Simulated by pointing the check at a closed port; the recorded tags stay as they were:

```text
$ BASE_URL=http://localhost:1 scripts/deploy.sh
...
urllib.error.URLError: <urlopen error [Errno 111] Connection refused>
verify failed for cccefb1; last verified: 48858cb (scripts/rollback.sh 48858cb)
$ cat .deploy/current .deploy/previous
48858cb
cccefb1
```

Then forward to the newest tag, verified this time:

```text
$ scripts/rollback.sh cccefb1
rolling back to cccefb1
verify: ok
running cccefb1
```

### Full restart keeps all data

```text
$ docker compose down && IMAGE_TAG=$(cat .deploy/current) docker compose up -d --wait
documents before: 15, after: 15; runs before: 414, after: 414
```

The 15 documents are the 14 corpus PDFs and the smoke test document.

### Redis outage

```text
$ docker compose stop redis
$ curl -s localhost:8080/api/ready
{"status":"degraded","checks":{"database":"up","redis":"down"}}
$ python3 scripts/ask.py "What are the four functions of the NIST AI RMF Core?"
status: complete
  tool search_documents {"query": "NIST AI RMF Core four functions GOVERN MAP MEASURE MANAGE", "top_k": 5} -> ok, 5 passages, cache unavailable, 322 ms
[1] NIST AI 100-1: Artificial Intelligence Risk Management Framework (AI RMF 1.0), January 2023, page 25 (doc 1, page 25) verified: "NIST AI 100-1 AI  ...
totals: 3607 ms, 2 model calls, 1 tool calls, $0.0011
$ docker compose start redis && curl -s localhost:8080/api/ready
{"status":"ok","checks":{"database":"up","redis":"up"}}
```

The only log line in the API during the outage was the expected warning:

```text
{"ts": "2026-10-28T06:07:06.943+00:00", "level": "WARNING", "logger": "app.cache", "msg": "redis unavailable; continuing without cache", "error": "network:TimeoutError", "retry_after_s": 30.0}
```

An earlier run of the same check also logged `Future exception was never retrieved` at ERROR. It came from uvloop (issue 437 in its tracker), so the API now runs on the standard asyncio loop.
