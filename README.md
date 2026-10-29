# Callslip

Callslip answers simple and multi-part questions across a set of text-based PDFs. An agent chooses its own tools (search, read pages, a document's outline, list documents, ask for clarification), looks at what it finds, and answers with document and page citations. Code checks that every quote is on the page it cites, and a second model call judges whether each quote supports its sentence.

**Try it:** https://callslip.apps.rm3.7wse.p1.openshiftapps.com

https://github.com/user-attachments/assets/e6142501-9f08-4a38-8f30-992d8bc2bf2d

The walkthrough above ([download](docs/media/callslip-walkthrough.mp4)) shows signing in and uploading a private PDF, a question across two documents, exporting the answer, both answering modes side by side, a second search driven by what the first found, a clarification, a failed search recovered through the document's outline, a question about the private PDF and its deletion, the saved conversations, and the Evaluation page.

The name comes from the call slip, the form a library reader fills in to have material brought from the stacks.

Start with [SUMMARY.md](SUMMARY.md): what was built, the results, and what is unfinished.

## Status

| Part | Status | Where to check |
|---|---|---|
| Expected components A to J of the brief: frontend and API, ingestion and retrieval, agent loop, tools, state and traces, limits and safety, PostgreSQL and Redis, Docker and CI, evaluation, engineering | Done | [docs/requirements.md](docs/requirements.md): each item with its code and its proof |
| The eight required behaviours | Done: each is an evaluation case; the agent passes 43 of 45 runs, the single pass 21 | [evaluation](docs/evaluation.md#results) |
| What to submit: repository, reproducibility notes, architecture diagram, evaluation with a baseline, walkthrough, summary, deployment runbook | Done | [reproducibility](docs/reproducibility.md), [architecture](docs/architecture.md), [evaluation](docs/evaluation.md), [walkthrough](docs/demo.md), [summary](SUMMARY.md), [runbook](docs/runbook.md) |
| Optional: authentication and personalisation | Done: local accounts, private uploads and their deletion, history per account, a limit on failed sign-ins | [accounts](#accounts-and-conversations) |
| Optional: advanced retrieval | Done: hybrid vector and full-text search; a reranker was measured and not kept | [evaluation](docs/evaluation.md#failure-analysis) |
| Optional: Kubernetes and OpenShift | Done: live on OpenShift, deployed with Terraform; also tested on a local kind cluster with network policies, update, rollback and pod loss | [live demo](https://callslip.apps.rm3.7wse.p1.openshiftapps.com), [docs/kubernetes.md](docs/kubernetes.md#live-on-openshift) |
| Optional: infrastructure as code | Done: Kustomize describes the workloads; Terraform makes the namespace and Secrets and applies them, on the kind cluster and on OpenShift | [docs/kubernetes.md](docs/kubernetes.md#apply-with-terraform) |
| Added beyond the brief | Compare mode (both answering modes side by side); export an answer with its sources; answers stream with live progress; a second model call checks every quote against its sentence; questions run in queued workers; each document's outline is a tool; internal metrics; a limit on questions per address; latency measured in a real browser | [summary](SUMMARY.md) |
| Not done | NYU single sign-on, sharing with groups, a production cluster with managed PostgreSQL, a larger evaluation | [summary](SUMMARY.md#unfinished-and-what-i-would-do-with-more-time) |

## Results at a glance

Fifteen evaluation cases, three repeats each, on the same corpus, model and retriever, recorded at commit `09d1b08` ([details](docs/evaluation.md)). With each document's outline added as a tool, the agent passed 44 of 45 ([run](eval/results/2026-10-28T221200Z/)), and the failed-search case 20 of 20. Scores use the checks after the [grader corrections](docs/evaluation.md#grader-corrections), applied to both systems. The current build passed all 45 runs ([details](docs/evaluation.md#results)).

| Claude Haiku 5.5 (the default) | Agent | Single-pass baseline |
|---|---|---|
| Runs passing every check | **43 of 45** | 21 of 45 |
| Citations found on the page they cite | 206 of 206 | 121 of 121 |
| Time to the full answer, median | 5.5 s | 5.2 s |
| Cost per question | $0.0020 | $0.0014 |

The difference is in the cases that need more than one step: two documents, a clarification, a second search for which memo governs, a tool that times out. The baseline fails all of them; both pass the single lookups. Because the agent searches independent parts in the same turn, its median time to answer is within half a second of the single pass.

## Documentation

| Document | What it covers |
|---|---|
| [docs/requirements.md](docs/requirements.md) | every requirement of the brief, where it is built, and what proves it works |
| [docs/architecture.md](docs/architecture.md) | services, data flow, the agent's tools, state and stopping conditions, trade-offs, scaling |
| [docs/demo.md](docs/demo.md) | the recorded walkthrough, and how to reproduce each step: multi-document question, re-retrieval, clarification, tool failure, limits, Redis outage |
| [docs/evaluation.md](docs/evaluation.md) | fifteen cases, the agent against a single-pass baseline, latency, the support check, failure analysis |
| [docs/runbook.md](docs/runbook.md) | deploy, verify, update, roll back, persistence, logging, with captured output |
| [docs/kubernetes.md](docs/kubernetes.md) | the same images on Kubernetes or OpenShift: manifests, how to deploy, what is checked |
| [docs/reproducibility.md](docs/reproducibility.md) | corpus sources and checksums, models, prompts, tool schemas, evaluation command, costs |

## Stack

| Service | What it does |
|---|---|
| `frontend` | React + TypeScript (Vite) app served by nginx on port 8080; nginx also proxies `/api` to the API |
| `api` | FastAPI: documents, hybrid search, accounts, sessions; queues each question and streams its steps to the UI as server-sent events; health and readiness |
| `runner` | Run workers: claim queued questions and run the agent or the single-pass baseline, streaming each step to the database |
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

A plain tool-use loop over the Claude Messages API (no agent framework), in `backend/app/agent/loop.py`. The first message lists the documents the user can search. Each turn the model sees the whole conversation and calls one or more tools, asks a clarifying question, or answers:

| Tool | Read-only? | What it returns |
|---|---|---|
| `list_documents()` | yes | JSON list of ready documents: id, title, page count |
| `search_documents(query, document_ids?, page_from?, page_to?, top_k?)` | yes | citable passages (`search_result` blocks), or `{"status": "no_results"}` |
| `read_document_section(document_id, page_start, page_end)` | yes | up to 3 full pages as citable passages |
| `document_outline(document_id)` | yes | the document's sections from its own PDF bookmarks, each with the page it starts on, or `{"status": "no_outline"}` |
| `ask_clarification(question, options?)` | control | pauses the run until the user replies |

Every tool input is validated (Pydantic); a bad call comes back as an error the model can fix. The read tools of one turn run at the same time, so a question with independent parts costs one turn, not one per part; a clarification is only asked on its own. Limits, all configurable: model turns (10), tool calls (9), per-tool timeout (8 s) with one retry, and a run deadline (90 s) with a reserve for the final answer. At a limit, the model must answer from what it has, marked incomplete; with no time left at all, the run stops with a summary of what it found and no further model call. Clarification pauses the run (`needs_clarification`); the reply resumes the same run, exactly once (idempotency key), and the time spent waiting does not count.

In the UI, choose Agent, Single pass or Compare at the top of the page; the line under the question box says what each does. Compare asks one question both ways at once and shows the two answers side by side, above a table of what differs: documents cited, sources, tool calls and time. While a question runs, the conversation lists each search and page read as it happens. From a terminal: `python3 scripts/ask.py "question" [--mode baseline] [--reply "answer to a clarifying question"]`.

## Answers and citations

Passages go to Claude (`claude-haiku-5-5` by default, `claude-sonnet-5-5` as an option; see [the comparison](docs/evaluation.md#which-model-and-why-haiku-is-the-default)) as `search_result` blocks with citations enabled, split into groups of a few sentences so a citation quotes only what it needs. Every citation in the answer is checked in code: it must point at a passage that was actually sent (same index, source and quoted blocks) and the quoted text must appear on the stored page. In the UI, each citation is a number after the text it supports. Selecting it opens that source in the side panel: the quote, the check result and a link that opens the PDF at that page. A cited piece of eight or more words that matches its source word for word, apart from spacing and line-break hyphens, is shown in quotation marks. Export saves a finished answer as Markdown: the question, the answer with its citation numbers, and each source with its page, quote, link and the results of both checks.

The answer is shown as the model writes it, then replaced by the checked answer with its citations. After that, one more model call (the support check) judges whether each quote supports the sentence it is cited for: supported, partly, or not supported. Its verdicts appear next to each source as advice; against 84 hand-labelled pieces, it judged none of the 24 altered or mismatched pieces supported ([evaluation](docs/evaluation.md)).

Each question is a run with its own state, stored in PostgreSQL: the exact model conversation (append-only), the steps shown in the interface, and every model call with tokens and estimated cost. A run worker executes it; the API only queues it and streams its events, so the API can run as several replicas. The interface shows the time to the answer, and the full time with the support check in the steps.

## Accounts and conversations

Without signing in, a browser gets a random token in an HttpOnly, SameSite=Strict cookie; its conversations belong to that token, so another browser cannot read them. Signing in (a local account, standing in for NYU single sign-on) adds two things:
- **Private documents.** Uploads belong to the account. Search, the agent's tools and citations see the shared collection plus the account's own documents, and nobody else's. The owner can delete them; their file and passages go too, and no cached search that included them is read again. Saved answers that quoted a deleted document keep those quotes.
- **Sign-in limits.** After five failed sign-ins for an email from one address within 15 minutes, that address is refused for that email until the window ends. This slows guessing from one address, not guessing spread over many addresses, and there is no limit while Redis is down. Nobody can lock an account by failing on purpose from elsewhere.
- **History that follows the account.** The Conversations tab lists earlier conversations, newest first; selecting one opens it with its answers, sources and steps, in any browser signed in to the account.

One question at a time per conversation.

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

Browser tests (Playwright, desktop and phone sizes) run against a running stack, such as `docker compose up`:

```bash
cd frontend
npx playwright install chromium
npm run e2e                      # BASE_URL=... to test another deployment
```

They cover the sign-in menu, a private upload seen only by its owner, plain messages for a wrong password, a file that is not a PDF and an unreachable server, and the phone layout. They need no model; with an API key set, run them with `HAS_MODEL=1`. CI runs them on every pull request.

## Search

Hybrid retrieval over the same filtered candidate set (ready documents, optional document ids and page range):
- **Meaning:** exact cosine similarity on pgvector embeddings. No approximate index: at a few thousand passages a full scan takes milliseconds and filters can never under-fill results.
- **Keywords:** PostgreSQL full-text search ranked by `ts_rank_cd` (cover density; not BM25).
- **Fusion:** reciprocal rank fusion (k=60), so a passage found by both ranks highest. Scores order results; they are not probabilities.

Redis caches search results and query embeddings, and counts failed sign-ins:

| Key | Holds | TTL and invalidation |
|---|---|---|
| `search:v1:{corpus_epoch}:{corpus_version}:{model}:{hash}` | results for a query, filters and top_k | 10 minutes; `corpus_version` increases in the same transaction that publishes a document, and `corpus_epoch` is a random id per database, so stale results are never read, even after the database is recreated (a restore from backup sets a new epoch, see the runbook) |
| `qemb:v1:{model}:{hash}` | a query's embedding | 24 hours; keyed by model |
| `login:fail:{sha256(email, client address)}` | failed sign-ins for one email from one address | 15 minutes from the first failure; after 5 that email is refused from that address until it expires; a successful sign-in deletes it |

If Redis is down, reads count as misses, writes are skipped, Redis is not retried for 30 seconds, and `/api/ready` reports `degraded`. Search keeps working, and sign-in works without the limit.

CI runs on every pull request: backend and script lint, tests against real PostgreSQL, Redis and the embedding model, frontend typecheck and build, a render and schema check of the Kubernetes manifests, then a Compose build, smoke test, full restart (data must survive) and a Redis outage (search must keep working).
