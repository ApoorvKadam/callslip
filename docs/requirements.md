# The brief, requirement by requirement

Each requirement of the take-home brief, where it is built, and what shows that it works. A proof is a test that runs in CI on every pull request, an evaluation case with saved traces, or output captured from the running stack.

## Expected components

| | Requirement | Where it is built | Proof |
|---|---|---|---|
| A | A frontend and a backend, kept apart; an API between them; a clean, usable UI | `frontend/` (React, TypeScript), `backend/app/api/` (FastAPI) | CI builds both images and runs the Compose smoke test; the [walkthrough video](media/callslip-walkthrough.mp4) |
| B | Parsing, chunking, indexing, retrieval and grounded answers, keeping document and page | `backend/app/ingest/` (pages, passages), `backend/app/retrieval/search.py` (hybrid search), `backend/app/agent/evidence.py` (citation checks) | tests `test_pdf`, `test_chunking`, `test_ingest_and_search`, `test_search`, `test_evidence`; in the final runs every one of 206 citations was found on the page it cites |
| C | A tool-use loop that splits questions, rewrites weak queries, combines documents, and changes course on what it finds | `backend/app/agent/loop.py`, `backend/app/agent/prompts.py` | evaluation cases 2 and 3 (one search per document), 9 (a second search for which memo governs), 8b (switches to reading pages when search fails), with [traces](evaluation.md#representative-traces) |
| D | Three or more read-only tools with structured input and output, validation, empty and error results | `backend/app/agent/tools.py`: `list_documents`, `search_documents`, `read_document_section`, plus `ask_clarification` | `test_tools` (invalid input, empty result, timeout, one retry), `test_agent_loop` |
| E | State per session: questions, tool results, evidence, clarifications; a trace with tool names, inputs, summaries, status, citations, timing and tokens | `backend/app/runs/` (stored messages and events), the Steps tab in the UI | `test_sessions`, `test_agent_loop`; every evaluation trace in `eval/results/` |
| F | Step limits, tool timeouts, bounded retries, a useful partial answer at a limit; retrieved text never followed as instructions; tools limited to the corpus; isolated sessions | `backend/app/config.py` (limits), `backend/app/agent/loop.py`, `backend/app/api/sessions.py`, `backend/app/api/auth.py` | `test_agent_loop` (limits, timeouts, forced final answer); evaluation cases 7 (planted instruction), 8a and 8b; `test_sessions` and `test_accounts` (other browsers and accounts get 404) |
| G | A database; Redis with a real purpose, its keys, expiry and invalidation, and behaviour when Redis is down | PostgreSQL holds everything; `backend/app/cache.py` caches searches and query embeddings ([keys and expiry](../README.md#search)) | `test_cache`; CI stops Redis and checks that search still works; [captured outage](runbook.md#redis-outage) |
| H | Dockerfiles, Compose, configuration, health checks, volumes, secrets, CI tests and builds; smoke test, persistence across restart, Redis outage, update and rollback | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `scripts/deploy.sh`, `rollback.sh`, `verify.sh`, `smoke_test.py` | CI on every pull request; [runbook evidence](runbook.md#evidence): update, rollback, a failed deploy, a full restart and a Redis outage |
| I | At least eight cases with expected behaviour and sources, actual results, failure analysis, a single-pass baseline on the same corpus and model, traces, exclusions | `eval/cases.json` (15 cases), `scripts/eval.py` | [docs/evaluation.md](evaluation.md): both models, both systems, three repeats, failure analysis, exclusions |
| J | Good engineering practice, organisation and documentation | one pull request per change, each squash-merged; lint and 121 backend tests | the git history and CI |

## The eight required behaviours

The Haiku agent on the final build, three repeats each ([run](../eval/results/2026-10-28T165727Z/)):

| | Behaviour | What must happen | Agent | Single pass |
|---|---|---|---|---|
| 1 | Simple lookup | cite the right passage and page | 3 of 3 | 3 of 3 |
| 2 | Multi-part, two documents | evidence from both documents | 3 of 3 | 0 of 3 |
| 3 | A second cross-document question | cite each supported claim | 3 of 3 | 0 of 3 |
| 4 | Ambiguous question | ask, then keep the context | 3 of 3 | 0 of 3 |
| 5 | Insufficient evidence | say what is missing, invent nothing | 3 of 3 | 0 of 3 |
| 6 | Conflicting sources | cite both, explain the uncertainty | 3 of 3 | 3 of 3 |
| 7 | Prompt injection in a document | ignore the planted instruction | 3 of 3 | 3 of 3 |
| 8 | Tool failure or timeout | retry within limits, recover or report | 8a: 3 of 3; 8b: 2 of 3 | 8a: 0 of 3; 8b: 3 of 3 |

Cases 9 to 14 add a conflict settled by supersession and five questions written after the prompt was tuned ([results](evaluation.md#results)).

## What to submit

| Item | Where |
|---|---|
| Repository with setup instructions | [README](../README.md#run-it) |
| Reproducibility notes: corpus, models, prompts, tool schemas, environment template, evaluation command, costs | [docs/reproducibility.md](reproducibility.md), `.env.example` |
| Architecture diagram: components, agent state, tool calls, decision points, retrieval loop, stopping conditions | [docs/architecture.md](architecture.md) |
| Agent and baseline results with failure analysis | [docs/evaluation.md](evaluation.md) |
| Recorded demo or walkthrough with traces and answers | [video](media/callslip-walkthrough.mp4), [docs/demo.md](demo.md) |
| Summary of what is done, unfinished and next | [SUMMARY.md](../SUMMARY.md) |
| Deployment runbook and evidence | [docs/runbook.md](runbook.md) |

## Optional enhancements

| Enhancement | State |
|---|---|
| Authentication and personalisation | Local accounts standing in for NYU single sign-on; private uploads that only their owner can see, search or cite; conversation history per account ([README](../README.md#accounts-and-conversations), `test_accounts`) |
| Advanced retrieval | Hybrid search: vector similarity and full-text, fused by rank. A cross-encoder reranker was measured and not kept ([evaluation](evaluation.md#failure-analysis)) |
| Kubernetes and OpenShift | Manifests with network policies in `deploy/kubernetes/`, rendered and schema-checked in CI; not run on a cluster ([docs/kubernetes.md](kubernetes.md)) |

Beyond the brief: answers stream as they are written; the conversation shows each step while the answer is on the way; a support check judges every quote against its sentence and is measured against 84 hand labels; questions run in queued workers so the API scales out; latency is measured in a real browser ([evaluation](evaluation.md#latency)).
