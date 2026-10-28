# Evaluation results, 2026-10-28T212457Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 4 of 6 | 12.7 | 10.9 | 3.8 | 5.8 | 40 of 40 | 29509 | 0.0155 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 13.6 | 10.9 | 3218/2074 | 0.0034 | recovered. |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 12.6 | 10.2 | 3507/2118 | 0.0027 | recovered. |
| 8b-tool-keeps-failing | agent | no | complete | 4/4 |  | 3 | 5 | 9.5 | 8.0 | 2009/1365 | 0.0019 | neither. failed check: recovered_or_reported_incomplete |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 14.1 | 11.3 | 3553/2117 | 0.0027 | recovered. |
| 8b-tool-keeps-failing | agent | no | complete | 5/5 |  | 4 | 6 | 13.0 | 11.1 | 2686/1775 | 0.0023 | neither. failed check: recovered_or_reported_incomplete |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 13.5 | 11.0 | 3066/2021 | 0.0026 | recovered. |
