# Evaluation runs

| Run | Answering model | Build | What it is |
|---|---|---|---|
| `2026-10-28T165727Z` | `claude-haiku-5-5` | final (main at `09d1b08`) | the default model; 15 cases, both systems, 3 repeats |
| `2026-10-28T171106Z` | `claude-sonnet-5-5` | final (main at `09d1b08`) | 15 cases, both systems, 3 repeats |
| `2026-10-28T163035Z` | `claude-haiku-5-5` | the latency change, before merging | agent only, answers at effort `low`; the support check also ran at `low` |
| `2026-10-28T162215Z` | `claude-haiku-5-5` | the latency change, before merging | agent only, answers at effort `medium` |
| `2026-10-28T152942Z` | `claude-haiku-5-5` | before the latency change (main at `66e3a1d`) | 15 cases, both systems, 3 repeats |
| `2026-10-28T154456Z` | `claude-sonnet-5-5` | before the latency change (main at `66e3a1d`) | 15 cases, both systems, 3 repeats |
| `2026-10-28T043802Z` | `claude-haiku-5-5` | the first ten cases | both systems, 3 repeats |
| `2026-10-28T044638Z` | `claude-sonnet-5-5` | the first ten cases | both systems, 3 repeats |

Each run used `python3 scripts/eval.py --repeat 3` (with `--systems agent` where noted) and `ANSWER_MODEL` set as shown. Runs from the fifteen-case set on were graded again with `--rescore` so every report gives the time to answer, measured from event times in the saved traces. The analysis is in [docs/evaluation.md](../../docs/evaluation.md).
