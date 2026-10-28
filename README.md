# Agentic RAG over PDFs

A full-stack application for asking simple and multi-part questions across a set of text-based PDFs. An agent chooses its own tools (search, read a section, list documents, ask for clarification), inspects what it finds, and answers with document and page citations that are checked against the source pages.

Status: in progress. This first part runs the whole stack and turns uploaded PDFs into searchable, page-tagged passages. Question answering, the agent loop, evaluation and full documentation follow in later changes.

## Stack

| Service | What it does |
|---|---|
| `frontend` | React + TypeScript (Vite) app served by nginx on port 8080; nginx also proxies `/api` to the API |
| `api` | FastAPI: document upload and listing, health and readiness |
| `worker` | Ingestion: parse each PDF page (pypdf), split pages into passages, embed them locally (fastembed, `BAAI/bge-small-en-v1.5`) |
| `postgres` | PostgreSQL 17 with pgvector: documents, raw files, pages, passages with vectors and full-text indexes |
| `redis` | Cache (search results and query embeddings); the app keeps working if it is down |

## Run it

Requirements: Docker with Compose v2.

```bash
cp .env.example .env          # then set POSTGRES_PASSWORD (and ANTHROPIC_API_KEY for answers)
docker compose up -d --build --wait
python3 scripts/smoke_test.py # health, readiness, upload, ingestion
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

Database tests need a PostgreSQL with pgvector; without `TEST_DATABASE_URL` they are skipped. For example:
`docker run -d --rm -p 55432:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_DB=ragtest pgvector/pgvector:0.8.7-pg17`.

Frontend (Node 24): `cd frontend && npm ci && npm run dev` (proxies `/api` to the stack on port 8080).

CI runs on every pull request: backend lint and tests against a real PostgreSQL, frontend typecheck and build, then a Compose build and smoke test.
