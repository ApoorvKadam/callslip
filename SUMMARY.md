# Summary

Callslip answers simple and multi-part questions over a set of PDFs. An agent picks its own tools, every quote in an answer is checked against the page it cites, and a second model call judges whether each quote supports its sentence.

## What was built

- **Six services in Docker Compose**: a React frontend behind nginx, a FastAPI API, run workers that execute questions, an ingestion worker, PostgreSQL 17 with pgvector, and Redis. Each has a health check and a memory limit, and secrets come only from `.env`. The same images have Kubernetes and OpenShift manifests, checked in CI.
- **Ingestion keeps page numbers exact.** The worker parses each upload page by page in a child process with time and memory limits, splits pages into passages measured in model tokens, embeds them locally, and publishes the document atomically while it holds a lease.
- **Hybrid retrieval**: pgvector similarity and PostgreSQL full-text search, fused by reciprocal rank, with document and page filters. Redis caches results under the corpus version, so a cached result never hides a newly published document.
- **The agent** is a plain tool-use loop on the Claude Messages API, with three read-only tools and a clarification tool. After each result it decides what to do next: search each document in the same turn, rewrite a weak query, read whole pages, ask which document the user means, or switch tools when one keeps failing.
- **Citations are checked in code.** Each quote must come from a passage that was sent and appear on the stored page. Then the support check judges each quote against its sentence; measured against 84 hand labels, it judged none of the 24 altered or mismatched pieces supported.
- **Execution safety**: limits on model turns, tool calls and time; a timeout and one retry per tool call; at a limit, an answer marked incomplete; text inside documents treated as evidence, never instructions.
- **Runs are queued.** The API records each question and returns; run workers claim it with a lease (`FOR UPDATE SKIP LOCKED`), so the API keeps no state and scales out. A run whose worker dies is closed, not run twice.
- **The interface streams** each step and the answer as it is written, shows each cited sentence's quote on its page, and keeps every conversation.
- **Accounts** (a local sign-in standing in for NYU single sign-on): uploads are private to their account, search and citations see only what the user may see, and history follows the account across browsers.
- **Measured, then made faster.** Running a turn's searches together, listing the documents up front and caching the conversation cut model turns per question from 3.4 to 2.4. With low effort for answers as well, the median time to the first answer text fell from 5.0 s to 3.6 s, and to the full answer from 6.8 s to 5.5 s.
- **Evaluation**: fifteen cases covering the eight required behaviours, five of them written after the prompt was tuned. The agent is compared with a single-pass baseline on the same corpus, model and retriever, three repeats, with saved traces.
- **Engineering**: one pull request per change, squash-merged; CI runs lint, tests against real PostgreSQL, Redis and the embedding model, the frontend build, image builds, a Kubernetes manifest check, and Compose smoke, restart and Redis-outage checks.

## Results

On fifteen cases with three repeats each, the agent on Claude Haiku 5.5 passed every check in 40 of 45 runs, against 21 of 45 for a single-pass baseline on the same retriever and model. Every citation was found on the page it cites. The baseline fails every case that needs a second step: two documents, a clarification, a tool that times out, which memo governs. The agent's median time to answer is 5.5 s, within half a second of the baseline, at $0.0020 per question. Claude Sonnet 5.5 also passed 40 of 45, at about twelve times the cost, so Haiku is the default and Sonnet a setting. Details: [docs/evaluation.md](docs/evaluation.md).

## Unfinished, and what I would do with more time

- **Retrieval quality.** Titles in passage headers help a query find the right document, but can also pull in front matter. Next: contextual chunk headers written at ingestion, and BM25 in place of `ts_rank_cd`, each kept only if the evaluation improves. A small cross-encoder reranker was measured and not kept.
- **Waking event streams by notification.** Each open stream polls its run's events; at many open streams, PostgreSQL `LISTEN` or Redis pub/sub would wake them instead.
- **Single sign-on.** The local accounts stand in for NYU SSO; sharing a document with a group is not built.
- **Running on a cluster.** The Kubernetes and OpenShift manifests are schema-checked in CI ([docs/kubernetes.md](docs/kubernetes.md)) but have not run on a cluster.
- **Evaluation size.** Fifteen cases on one corpus show clear differences between the agent and the baseline, not small ones between settings. Next: more questions written by people who did not build the system.
- Edge cases in run handling and ingestion, each with its fix: [docs/architecture.md](docs/architecture.md#known-limits).
