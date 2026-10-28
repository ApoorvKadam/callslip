# Agentic RAG over PDFs

A full-stack application for asking simple and multi-part questions across a set of text-based PDFs. An agent chooses its own tools (search, read a section, list documents, ask for clarification), inspects what it finds, and answers with document and page citations that are checked against the source pages.

Status: in progress. The stack runs end to end: uploaded PDFs become page-tagged passages, and hybrid search (meaning plus keywords) finds them. Question answering, the agent loop, evaluation and full documentation follow in later changes.

## Stack

| Service | What it does |
|---|---|
| `frontend` | React + TypeScript (Vite) app served by nginx on port 8080; nginx also proxies `/api` to the API |
| `api` | FastAPI: document upload and listing, hybrid search (`POST /api/search`), health and readiness |
| `worker` | Ingestion: parse each PDF page (pypdf), split pages into passages, embed them locally (fastembed, `BAAI/bge-small-en-v1.5`) |
| `postgres` | PostgreSQL 17 with pgvector: documents, raw files, pages, passages with vectors and full-text indexes |
| `redis` | Cache (search results and query embeddings); the app keeps working if it is down |

## Run it

Requirements: Docker with Compose v2.

```bash
cp .env.example .env          # then set POSTGRES_PASSWORD (and ANTHROPIC_API_KEY for answers)
docker compose up -d --build --wait
python3 scripts/smoke_test.py # health, readiness, upload, ingestion, search
```

Open http://localhost:8080 and upload PDFs. Each document moves from queued to processing to ready; failures show their reason.

## Develop

Backend (Python 3.12, [uv](https://docs.astral.sh/uv/)):

```bash
cd backend
uv sync
uv run ruff check . && uv run ruff format --check .
TEST_DATABASE_URL=postgresql://postgres:test@localhost:55432/ragtest uv run pytest
```

Tests use real services, never mocks, and skip what is not available:
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
| `search:v1:{corpus_epoch}:{corpus_version}:{model}:{hash}` | results for a query, filters and top_k | 10 minutes; `corpus_version` increases in the same transaction that publishes a document, and `corpus_epoch` is a random id per database, so stale results are never read, even after the database is recreated or restored |
| `qemb:v1:{model}:{hash}` | a query's embedding | 24 hours; keyed by model |

If Redis is down, reads count as misses, writes are skipped, Redis is not retried for 30 seconds, and `/api/ready` reports `degraded`. Search keeps working.

CI runs on every pull request: backend lint and tests against real PostgreSQL, Redis and the embedding model, frontend typecheck and build, then a Compose build and smoke test.
