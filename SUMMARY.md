# Summary

Callslip answers simple and multi-part questions over a set of PDFs. An agent picks its own tools, and every citation in an answer is checked against the page it names.

## What was built

- Five services in Docker Compose: a React frontend behind nginx, a FastAPI API, an ingestion worker, PostgreSQL 17 with pgvector, and Redis. Each has a health check and a memory limit, and secrets come only from `.env`.
- Ingestion keeps page numbers exact. The worker parses each upload page by page in a child process with time and memory limits, splits pages into passages measured in model tokens, embeds them locally, and publishes the document atomically while it holds a lease.
- Retrieval is hybrid: pgvector similarity and PostgreSQL full-text search, fused by reciprocal rank, with document and page filters. Redis caches results under the corpus version, so an older cached result never hides a newly published document.
- The agent is a plain tool-use loop on the Claude Messages API, with three read-only tools and a clarification tool. After each result it decides what to do next: narrow a search to one document, rewrite a weak query, read whole pages, ask which document the user means, or switch tools when one keeps failing.
- Passages go to Claude as `search_result` blocks. Each citation that comes back is checked against the passages actually sent and the stored page text. In the interface, each cited sentence leads to its source: the quote, the page check and a link to the page.
- Every run has limits on model turns, tool calls and wall-clock time. Each tool call has a timeout, and a timeout or a lost database connection gets one retry. At a limit the answer says it is incomplete, and no model call starts once time is up.
- Each run's exact model conversation, trace events and model calls (tokens and cost) are stored. The interface streams each step as it happens and picks up again after a refresh.
- The evaluation has ten cases that cover the eight required behaviours. It compares the agent with a single-pass baseline on the same corpus, model and retriever, with deterministic checks, three repeats and saved traces.
- The work went in as small pull requests. CI runs lint, tests against real PostgreSQL, Redis and the embedding model, the frontend build, the image builds, a Kubernetes manifest check, and Compose smoke, restart and Redis-outage checks.

## Results

On 10 cases with 3 repeats each, the agent on Claude Haiku 5.5 passed every check in 30 of 30 runs, against 11 of 30 for a single-pass baseline on the same retriever and model, at $0.0026 per question; every citation was verified on its page. On Claude Sonnet 5.5 the agent passed 27 of 30 at ten times the cost: it never searched for the page that settles which memo governs. Haiku is the default; Sonnet remains a setting. Details: [docs/evaluation.md](docs/evaluation.md).

## Unfinished, and what I would do with more time

- Claim-level support. Code verifies where each quote comes from; whether a cited passage supports its sentence was reviewed by hand. Next: an LLM judge checked against hand labels, reported separately.
- Retrieval quality. Titles in passage headers help a query find the right document, but can also pull in front matter. Next: contextual chunk headers written at ingestion, and BM25 in place of `ts_rank_cd`, each kept only if the evaluation improves. A small cross-encoder reranker was measured and not kept (see the evaluation).
- Streaming the answer text token by token. Steps stream today; the answer arrives whole.
- Scaling the API out. Runs execute as background tasks in the API process. Next: a run queue with its own workers, and Redis pub/sub for live events.
- Authentication (NYU SSO) and per-user collections. In this single-tenant demo, everyone shares the documents.
- Running on a cluster. The Kubernetes and OpenShift manifests are schema-checked in CI ([docs/kubernetes.md](docs/kubernetes.md)) but have not run on a cluster. The API needs the run queue before it can run more than one replica.
- A recorded video. The walkthrough in [docs/demo.md](docs/demo.md) can be reproduced from saved traces and commands.
