# Evaluation runs

| Run | Answering model | Notes |
|---|---|---|
| `2026-10-28T043802Z` | `claude-haiku-5-5` | the default model; both systems, 3 repeats |
| `2026-10-28T044638Z` | `claude-sonnet-5-5` | same build and prompts; both systems, 3 repeats |

Both runs used `python3 scripts/eval.py --repeat 3` with `ANSWER_MODEL` set as shown. Newer runs also record the model in `results.json` (`models`). The analysis is in [docs/evaluation.md](../../docs/evaluation.md).
