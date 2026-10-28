# Evaluation results, 2026-10-28T181548Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 36 of 45 | 6.4 | 4.2 | 1.6 | 3.1 | 179 of 179 | 141677 | 0.0701 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 5.4 | 3.1 | 1742/659 | 0.0011 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 4.8 | 3.2 | 1998/862 | 0.0008 |  |
| 3-multi-doc-b | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 6.2 | 4.0 | 3028/1284 | 0.0020 |  |
| 4-ambiguous | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 6.4 | 4.8 | 2628/1252 | 0.0019 | asked: Which memo do you mean? Several OMB AI memos are in the collection, and I want to check the right one for a 180-day requirement. |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 5.4 | 4.0 | 1753/828 | 0.0022 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 6.0 | 4.2 | 1993/1008 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 6.5 | 3.7 | 3191/1200 | 0.0013 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 16.1 | 12.7 | 4703/1786 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | no | complete | 0/0 |  | 2 | 3 | 3.6 | 3.6 | 8/444 | 0.0003 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 6.6 | 4.5 | 2946/1151 | 0.0016 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 6.4 | 4.8 | 1315/646 | 0.0021 |  |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.4 | 4.8 | 2415/1126 | 0.0022 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 3.9 | 2.4 | 1644/567 | 0.0014 |  |
| 13-security-and-injection | agent | no | complete | 8/8 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.8 | 4.9 | 3412/1419 | 0.0026 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.5 | 2.9 | 1326/505 | 0.0014 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 5.6 | 4.3 | 1776/690 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 4.8 | 3.0 | 1664/735 | 0.0007 |  |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 2 | 3 | 6.6 | 4.3 | 3083/1313 | 0.0024 |  |
| 4-ambiguous | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.0 | 5.0 | 2631/1274 | 0.0018 | asked: Which memo do you mean? Several OMB AI memos could have 180-day requirements. |
| 5-insufficient-evidence | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.5 | 4.3 | 2248/1131 | 0.0023 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 5.5 | 4.1 | 2031/1057 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 2 | 3 | 6.7 | 3.7 | 2873/982 | 0.0011 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.6 | 12.6 | 4159/1594 | 0.0013 |  |
| 8b-tool-keeps-failing | agent | no | complete | 0/0 |  | 2 | 3 | 3.6 | 3.6 | 8/474 | 0.0004 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.9 | 4.4 | 2401/1185 | 0.0025 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 8.7 | 7.3 | 1321/712 | 0.0020 |  |
| 11-acquisition-supersession | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.0 | 4.9 | 1723/983 | 0.0019 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.2 | 2.4 | 1734/620 | 0.0006 |  |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 6.1 | 4.2 | 3027/1247 | 0.0024 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 3.6 | 2.5 | 1320/504 | 0.0012 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.4 | 3.2 | 1744/677 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 5.6 | 3.5 | 1651/720 | 0.0007 |  |
| 3-multi-doc-b | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 5.5 | 3.8 | 2532/1116 | 0.0022 |  |
| 4-ambiguous | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.8 | 5.5 | 2569/1282 | 0.0019 | asked: Which memo do you mean? Several documents in the collection are OMB memos that may contain 180-day requirements. |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 5.4 | 3.7 | 1726/868 | 0.0021 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 5.7 | 4.3 | 1982/971 | 0.0013 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 5.3 | 3.1 | 3191/985 | 0.0009 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.6 | 12.2 | 3240/1401 | 0.0019 |  |
| 8b-tool-keeps-failing | agent | no | complete | 0/0 |  | 2 | 3 | 3.9 | 3.9 | 8/500 | 0.0004 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 6.9 | 5.1 | 2600/1105 | 0.0017 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 5.6 | 4.3 | 1321/624 | 0.0020 |  |
| 11-acquisition-supersession | agent | yes | complete | 7/7 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 7.0 | 4.8 | 3144/1289 | 0.0024 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.3 | 3.1 | 1338/468 | 0.0011 |  |
| 13-security-and-injection | agent | no | complete | 9/9 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 8.7 | 5.0 | 3825/1671 | 0.0024 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.0 | 2.7 | 1314/476 | 0.0012 |  |
