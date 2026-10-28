# Evaluation runs

| Run | Answering model | Build | What it is |
|---|---|---|---|
| `2026-10-28T165727Z` | `claude-haiku-5-5` | final (main at `09d1b08`) | the default model; 15 cases, both systems, 3 repeats |
| `2026-10-28T171106Z` | `claude-sonnet-5-5` | final (main at `09d1b08`) | 15 cases, both systems, 3 repeats |
| `2026-10-28T192415Z` | `claude-haiku-5-5` | thinking guided by the documented prompt, two more instructions (kept) | agent only |
| `2026-10-28T221200Z` | `claude-haiku-5-5` | each document's outline as a tool (kept) | agent only |
| `2026-10-28T220519Z` | `claude-haiku-5-5` | each document's outline, cases 8b and 13 only (kept) | agent only, 20 repeats (`--cases 8b-tool-keeps-failing,13-security-and-injection --repeat 20`) |
| `2026-10-28T211637Z` | `claude-haiku-5-5` | read on to the section when search fails, first wording (not kept) | agent only |
| `2026-10-28T212651Z` | `claude-haiku-5-5` | read on to the section when search fails, second wording (not kept) | agent only |
| `2026-10-28T212457Z` | `claude-haiku-5-5` | second wording, case 8b only (not kept) | agent only, 6 repeats (`--cases 8b-tool-keeps-failing --repeat 6`) |
| `2026-10-28T184548Z` | `claude-haiku-5-5` | shorter answers (not kept) | agent only |
| `2026-10-28T183723Z` | `claude-haiku-5-5` | a search before the first turn, thinking off, two more instructions (not kept) | agent only |
| `2026-10-28T182823Z` | `claude-haiku-5-5` | a search on the question before the first turn (not kept) | agent only |
| `2026-10-28T181548Z` | `claude-haiku-5-5` | faster text delivery, thinking turned off (not kept) | agent only |
| `2026-10-28T163035Z` | `claude-haiku-5-5` | the latency change, before merging | agent only, answers at effort `low`; the support check also ran at `low` |
| `2026-10-28T162215Z` | `claude-haiku-5-5` | the latency change, before merging | agent only, answers at effort `medium` |
| `2026-10-28T152942Z` | `claude-haiku-5-5` | before the latency change (main at `66e3a1d`) | 15 cases, both systems, 3 repeats |
| `2026-10-28T154456Z` | `claude-sonnet-5-5` | before the latency change (main at `66e3a1d`) | 15 cases, both systems, 3 repeats |
| `2026-10-28T043802Z` | `claude-haiku-5-5` | the first ten cases | both systems, 3 repeats |
| `2026-10-28T044638Z` | `claude-sonnet-5-5` | the first ten cases | both systems, 3 repeats |

Each run used `python3 scripts/eval.py --repeat 3` (with `--systems agent` where noted) and `ANSWER_MODEL` set as shown. Runs from the fifteen-case set on were graded again with `--rescore` so every report gives the time to answer, measured from event times in the saved traces. Each `report.md` has the summary, one row per run, and then, case by case, the question, what was expected, and what each system answered in its first repeat. The analysis is in [docs/evaluation.md](../../docs/evaluation.md).
