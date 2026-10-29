# The brief, requirement by requirement

Each requirement of the take-home brief, where it is built, and what shows that it works. A proof is a test that runs in CI on every pull request, an evaluation case with saved traces, or output captured from the running stack.

## Problem statement

| Requirement | Where it is met |
|---|---|
| About 8 to 15 text-based PDFs from one domain, public or synthetic, included or with download instructions | 14 PDFs on US AI governance: 11 public documents and 3 synthetic Northbridge University policies, in `corpus/pdfs/`, each with its source link and SHA-256 in `corpus/manifest.json` ([reproducibility](reproducibility.md)) |
| Documents that support cross-document questions | evaluation cases 2, 3, 6, 9 and 13 each need two documents |
| Users upload documents and ask simple or multi-part questions | the Upload button (shared, or private when signed in) and the question box; `POST /api/documents`, `POST /api/sessions/{id}/runs` |
| The agent chooses tools, inspects results, and retrieves more, asks for clarification, or answers with document and page citations | `backend/app/agent/loop.py`; cases 4 (asks), 9 and 10 (searches again), every answer cites document and page |
| A single agent; a working containerized deployment; unfinished work documented | one agent; the whole stack in Docker Compose ([runbook](runbook.md)); [SUMMARY.md](../SUMMARY.md#unfinished-and-what-i-would-do-with-more-time) |

## Expected components

| | Requirement | Where it is built | Proof |
|---|---|---|---|
| A | A frontend and a backend, kept apart; an API between them; a clean, usable UI | `frontend/` (React, TypeScript), `backend/app/api/` (FastAPI) | CI builds both images and runs the Compose smoke test; the [walkthrough video](media/callslip-walkthrough.mp4) |
| B | Parsing, chunking, indexing, retrieval and grounded answers, keeping document and page | `backend/app/ingest/` (pages, passages), `backend/app/retrieval/search.py` (hybrid search), `backend/app/agent/evidence.py` (citation checks) | tests `test_pdf`, `test_chunking`, `test_ingest_and_search`, `test_search`, `test_evidence`; in the final runs every one of 206 citations was found on the page it cites |
| C | A tool-use loop that splits questions, rewrites weak queries, combines documents, and changes course on what it finds | `backend/app/agent/loop.py`, `backend/app/agent/prompts.py` | evaluation cases 2 and 3 (one search per document), 10 (a query rewritten after weak results), 9 (a second search for which memo governs), 8b (uses the document's outline and reads the section when search fails), with [traces](evaluation.md#representative-traces) |
| D | Three or more read-only tools with structured input and output, validation, empty and error results | `backend/app/agent/tools.py`: `list_documents`, `search_documents`, `read_document_section`, `document_outline`, plus `ask_clarification` | `test_tools` (invalid input, empty result, timeout, one retry), `test_agent_loop` |
| E | State per session: questions, tool results, evidence, clarifications; a trace with tool names, inputs, summaries, status, citations, timing and tokens | `backend/app/runs/` (stored messages and events), the Steps tab in the UI (each tool step folds out to its exact tool name, input and status) | `test_sessions`, `test_agent_loop`; every evaluation trace in `eval/results/` |
| F | Step limits, tool timeouts, bounded retries, a useful partial answer at a limit; retrieved text never followed as instructions; tools limited to the corpus; isolated sessions | `backend/app/config.py` (limits), `backend/app/agent/loop.py`, `backend/app/api/sessions.py`, `backend/app/api/auth.py` | `test_agent_loop` (limits, timeouts, forced final answer); evaluation cases 7 (planted instruction), 8a and 8b; `test_sessions` and `test_accounts` (other browsers and accounts get 404) |
| G | A database; Redis with a real purpose, its keys, expiry and invalidation, and behaviour when Redis is down | PostgreSQL holds everything; `backend/app/cache.py` caches searches and query embeddings ([keys and expiry](../README.md#search)) | `test_cache`; CI stops Redis and checks that search still works; [captured outage](runbook.md#redis-outage) |
| H | Dockerfiles, Compose, configuration, health checks, volumes, secrets, CI tests and builds; smoke test, persistence across restart, Redis outage, update and rollback | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `scripts/deploy.sh`, `rollback.sh`, `verify.sh`, `smoke_test.py` | CI on every pull request; [runbook evidence](runbook.md#evidence): update, rollback, a failed deploy, a full restart and a Redis outage |
| I | At least eight cases with expected behaviour and sources, actual results, failure analysis, a single-pass baseline on the same corpus and model, traces, exclusions | `eval/cases.json` (15 cases), `scripts/eval.py` | [docs/evaluation.md](evaluation.md): both models, both systems, three repeats, failure analysis, exclusions; each run's `report.md` lists every case's expected behaviour and actual answer |
| J | Good engineering practice, organisation and documentation | one pull request per change, each squash-merged; lint and 140 backend tests | the git history and CI |

## The eight required behaviours

Three repeats each, Claude Haiku 5.5. The first two columns are the recorded comparison at commit `09d1b08` ([run](../eval/results/2026-10-28T165727Z/)); the last is the agent on the current build ([run](../eval/results/2026-10-29T065232Z/)).

| | Behaviour | What must happen | Agent | Single pass | Agent, current build |
|---|---|---|---|---|---|
| 1 | Simple lookup | cite the right passage and page | 3 of 3 | 3 of 3 | 3 of 3 |
| 2 | Multi-part, two documents | evidence from both documents | 3 of 3 | 0 of 3 | 3 of 3 |
| 3 | A second cross-document question | cite each supported claim | 3 of 3 | 0 of 3 | 3 of 3 |
| 4 | Ambiguous question | ask, then keep the context | 3 of 3 | 0 of 3 | 3 of 3 |
| 5 | Insufficient evidence | say what is missing, invent nothing | 3 of 3 | 0 of 3 | 3 of 3 |
| 6 | Conflicting sources | cite both, explain the uncertainty | 3 of 3 | 3 of 3 | 3 of 3 |
| 7 | Prompt injection in a document | ignore the planted instruction | 3 of 3 | 3 of 3 | 3 of 3 |
| 8 | Tool failure or timeout | retry within limits, recover or report | 8a: 3 of 3; 8b: 2 of 3 | 8a: 0 of 3; 8b: 3 of 3 | 8a: 3 of 3; 8b: 3 of 3 |

On the current build the agent passed all 45 runs of the fifteen cases, and the single pass 20. Earlier builds passed 43 and 44 of 45; case 8b alone, run 20 times, passed 20.

For every case and run, the brief's fields are recorded: expected behaviour, actual answer, citations, pass or fail, tool calls, latency, tokens and a failure note (each run's `report.md`). For each system: correctness, citation support, task completion, tool calls, latency and cost ([results](evaluation.md#results); citation support in [the support check](evaluation.md#hand-review-the-ten-case-runs-first-repeat)). Where the agent helps and where it only adds cost: [evaluation](evaluation.md#where-the-agent-helps-and-where-it-only-adds-cost).

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
| Authentication and personalisation | Local accounts standing in for NYU single sign-on; private uploads that only their owner can see, search, cite or delete; a limit on failed sign-ins; conversation history per account ([README](../README.md#accounts-and-conversations), `test_accounts`) |
| Advanced retrieval | Hybrid search: vector similarity and full-text, fused by rank; each document's outline (its PDF bookmarks) for navigating to a section. A cross-encoder reranker was measured and not kept ([evaluation](evaluation.md#failure-analysis)) |
| Infrastructure as code | The Kubernetes and OpenShift manifests (Kustomize base and three overlays) describe the workloads; Terraform makes the namespace and Secrets and applies an overlay, used on the kind cluster and for the OpenShift deployment ([docs/kubernetes.md](kubernetes.md#apply-with-terraform)) |
| Kubernetes and OpenShift | Manifests with probes, limits, non-root containers and network policies in `deploy/kubernetes/`, rendered and schema-checked in CI; run on a local kind cluster with the browser check, network policies, update, rollback and pod loss tested; live on OpenShift, deployed with Terraform ([docs/kubernetes.md](kubernetes.md#live-on-openshift)) |

Beyond the brief: a compare mode asks one question both ways at once and shows what each found; any answer exports as Markdown with its sources and checks; answers stream as they are written; the conversation shows each step while the answer is on the way; a support check judges every quote against its sentence and is measured against 84 hand labels; questions run in queued workers so the API scales out; owners delete their uploads, and failed sign-ins are limited; the API serves internal Prometheus metrics for queue wait, run time and model cost ([runbook](runbook.md#metrics)); questions are limited per client address on shared deployments; latency is measured in a real browser ([evaluation](evaluation.md#latency)).
