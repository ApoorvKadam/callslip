# Agentic RAG over PDFs

A full-stack application for asking simple and multi-part questions across a set of text-based PDFs. An agent chooses its own tools (search, read a section, list documents, ask for clarification), inspects what it finds, and answers with document and page citations that are checked against the source pages.

Start with [SUMMARY.md](SUMMARY.md): what was built, the results in one paragraph, and what is unfinished.

| Document | What it covers |
|---|---|
| [docs/architecture.md](docs/architecture.md) | services, data flow, the agent's tools, state and stopping conditions, trade-offs, scaling |
| [docs/demo.md](docs/demo.md) | a reproducible walkthrough: multi-document question, re-retrieval, clarification, tool failure, limits, Redis outage |
| [docs/evaluation.md](docs/evaluation.md) | ten cases, the agent against a single-pass baseline, failure analysis |
| [docs/runbook.md](docs/runbook.md) | deploy, verify, update, roll back, persistence, logging, with captured output |
| [docs/kubernetes.md](docs/kubernetes.md) | the same images on Kubernetes or OpenShift: manifests, how to deploy, what is checked |
| [docs/reproducibility.md](docs/reproducibility.md) | corpus sources and checksums, models, prompts, tool schemas, evaluation command, costs |

## Stack

| Service | What it does |
|---|---|
| `frontend` | React + TypeScript (Vite) app served by nginx on port 8080; nginx also proxies `/api` to the API |
| `api` | FastAPI: documents, hybrid search, sessions and question runs (executed in the background, streamed to the UI as server-sent events), health and readiness |
| `worker` | Ingestion: parse each PDF page (pypdf), split pages into passages, embed them locally (fastembed, `BAAI/bge-small-en-v1.5`) |
| `postgres` | PostgreSQL 17 with pgvector: documents, raw files, pages, passages with vectors and full-text indexes |
| `redis` | Cache (search results and query embeddings); the app keeps working if it is down |

## Run it

Requirements: Docker with Compose v2.

```bash
cp .env.example .env          # then set POSTGRES_PASSWORD (and ANTHROPIC_API_KEY for answers)
docker compose up -d --build --wait
python3 scripts/smoke_test.py # health, readiness, upload, ingestion, search
python3 scripts/load_corpus.py # optional: the 14 PDFs used in the evaluation
```

`scripts/deploy.sh` does the same with images tagged by commit, and `scripts/rollback.sh` goes back to the previous tag ([runbook](docs/runbook.md)).

Open http://localhost:8080, upload PDFs and ask questions. Each document moves from queued to processing to ready; failures show their reason. From a terminal: `python3 scripts/ask.py "your question"` prints the answer, each citation with its page and check result, and the run's steps, time, tokens and cost.

## The agent

A plain tool-use loop over the Claude Messages API (no agent framework), in `backend/app/agent/loop.py`. Each turn the model sees the whole conversation and picks one action:

| Tool | Read-only? | What it returns |
|---|---|---|
| `list_documents()` | yes | JSON list of ready documents: id, title, page count |
| `search_documents(query, document_ids?, page_from?, page_to?, top_k?)` | yes | citable passages (`search_result` blocks), or `{"status": "no_results"}` |
| `read_document_section(document_id, page_start, page_end)` | yes | up to 3 full pages as citable passages |
| `ask_clarification(question, options?)` | control | pauses the run until the user replies |

Every tool input is validated (Pydantic); a bad call comes back as an error the model can fix. One tool call per turn keeps the order simple and a clarification never mixed with other calls. Limits, all configurable: model turns (10), tool calls (9), per-tool timeout (8 s) with one retry, and a run deadline (90 s) with a reserve for the final answer. At a limit, the model must answer from what it has, marked incomplete; with no time left at all, the run stops with a summary of what it found and no further model call. Clarification pauses the run (`needs_clarification`); the reply resumes the same run, exactly once (idempotency key), and the time spent waiting does not count.

In the UI, choose Agent or Single pass under the question box. From a terminal: `python3 scripts/ask.py "question" [--mode baseline] [--reply "answer to a clarifying question"]`.

## Answers and citations

Passages go to Claude (`claude-haiku-5-5` by default, `claude-sonnet-5-5` as an option; see [the comparison](docs/evaluation.md#which-model-and-why-haiku-is-the-default)) as `search_result` blocks with citations enabled, split into groups of a few sentences so a citation quotes only what it needs. Every citation in the answer is checked in code: it must point at a passage that was actually sent (same index, source and quoted blocks) and the quoted text must appear on the stored page. The UI shows each citation as a numbered chip; selecting it shows the quote, the check result and a link that opens the PDF at that page.

Each question is a run with its own state, stored in PostgreSQL: the exact model conversation (append-only), the steps shown in the trace, and every model call with tokens and estimated cost. A browser gets a random token in an HttpOnly, SameSite=Strict cookie; sessions and runs belong to it, so another browser cannot read them. One question at a time per session.

## Develop

Backend (Python 3.12, [uv](https://docs.astral.sh/uv/)):

```bash
cd backend
uv sync
uv run ruff check . && uv run ruff format --check .
TEST_DATABASE_URL=postgresql://postgres:test@localhost:55432/ragtest uv run pytest
```

Tests use real PostgreSQL, Redis and the embedding model, and skip what is not available. They never call the model: agent and citation tests replay recorded real model output.
- `TEST_DATABASE_URL`: PostgreSQL with pgvector, e.g. `docker run -d --rm -p 55432:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_DB=ragtest pgvector/pgvector:0.8.7-pg17`
- `TEST_REDIS_URL`: e.g. `docker run -d --rm -p 56379:6379 redis:8.2-alpine` and `redis://localhost:56379/0`
- `FASTEMBED_CACHE_PATH`: a folder holding the embedding model, downloaded once with
  `uv run python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='$FASTEMBED_CACHE_PATH')"`

Frontend (Node 24): `cd frontend && npm ci && npm run dev` (proxies `/api` to the stack on port 8080).

## Search

Hybrid retrieval over the same filtered candidate set (ready documents, optional document ids and page range):
- **Meaning:** exact cosine similarity on pgvector embeddings. No approximate index: at a few thousand passages a full scan takes milliseconds and filters can never under-fill results.
- **Keywords:** PostgreSQL full-text search ranked by `ts_rank_cd` (cover density; not BM25).
- **Fusion:** reciprocal rank fusion (k=60), so a passage found by both ranks highest. Scores order results; they are not probabilities.

Redis caches search results and query embeddings:

| Key | Holds | TTL and invalidation |
|---|---|---|
| `search:v1:{corpus_epoch}:{corpus_version}:{model}:{hash}` | results for a query, filters and top_k | 10 minutes; `corpus_version` increases in the same transaction that publishes a document, and `corpus_epoch` is a random id per database, so stale results are never read, even after the database is recreated (a restore from backup sets a new epoch, see the runbook) |
| `qemb:v1:{model}:{hash}` | a query's embedding | 24 hours; keyed by model |

If Redis is down, reads count as misses, writes are skipped, Redis is not retried for 30 seconds, and `/api/ready` reports `degraded`. Search keeps working.

CI runs on every pull request: backend and script lint, tests against real PostgreSQL, Redis and the embedding model, frontend typecheck and build, then a Compose build, smoke test, full restart (data must survive) and a Redis outage (search must keep working).
