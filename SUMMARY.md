# Summary

## What was built

- **A working, containerized application**: five services in Docker Compose (React frontend behind nginx, FastAPI API, ingestion worker, PostgreSQL 17 with pgvector, Redis), each with a health check, a memory limit and secrets only from `.env`.
- **Ingestion that keeps page numbers exact**: uploads are parsed page by page in a child process with time and memory limits, split into page-bounded passages measured in model tokens, embedded locally, and published atomically by a worker holding a lease.
- **Hybrid retrieval**: exact pgvector similarity plus PostgreSQL full-text, fused by reciprocal rank, with document and page filters; a Redis cache keyed by corpus version, so a newly published document is never hidden by an older cached result.
- **An agent, not a pipeline**: a plain tool-use loop over the Claude Messages API with three read-only tools and a clarification tool. It decides after every result: it narrows searches to the right document, rewrites weak queries, reads whole pages, asks which document the user means, and switches tools when one keeps failing.
- **Citations that are checked, not trusted**: passages go to Claude as `search_result` blocks; every returned citation is verified against the evidence actually sent and the stored page text, and the UI shows the quote, the check result and a link to the page.
- **Bounded execution**: caps on model turns, tool calls and wall-clock time, per-tool timeouts with one retry, an honest incomplete answer at a limit, and no model call at all when time is up.
- **State and observability**: every run's exact conversation, trace events and model calls (tokens, cost) are stored; the UI streams each step live and recovers after a refresh.
- **Evaluation**: ten cases covering the eight required behaviours, the agent against a single-pass baseline on the same corpus, model and retriever, with deterministic checks, three repeats and saved traces.
- **Engineering process**: small pull requests with CI (lint, tests against real PostgreSQL, Redis and the embedding model; frontend build; image builds; Compose smoke, restart and Redis-outage checks), each reviewed before merging.

## Results in one line

On 10 cases with 3 repeats each, the agent on Claude Haiku 5.5 passed every check in 30 of 30 runs, against 11 of 30 for a single-pass baseline on the same retriever and model, at $0.0026 per question; every citation was verified on its page. On Claude Sonnet 5.5 the agent passed 27 of 30 at ten times the cost: it never searched for the page that settles which memo governs. Haiku is the default; Sonnet remains a setting. Details: [docs/evaluation.md](docs/evaluation.md).

## Unfinished, and what I would do with more time

- **Claim-level support checking**: provenance is verified in code; whether each cited passage supports its sentence is reviewed by hand. Next: an LLM judge validated against hand labels, reported separately.
- **Retrieval quality**: titles in passage headers help a query find the right document but can also pull in front matter. Next: contextual chunk headers generated at ingestion, a reranker, and BM25 in place of `ts_rank_cd`, each kept only if the evaluation improves.
- **Token-by-token streaming** of the answer text (steps stream today; the answer arrives whole).
- **Scaling the API out**: runs execute as background tasks in the API process. Next: a run queue with dedicated workers and Redis pub/sub for live events.
- **Authentication** (NYU SSO) and per-user document collections; documents are shared in this single-tenant demo.
- **Kubernetes or OpenShift manifests**: the services and health endpoints map directly; not written.
- **A recorded video**: the walkthrough is reproducible from saved traces and commands (`docs/demo.md`).
