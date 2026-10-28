# Evaluation results, 2026-10-28T183723Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 28 of 45 | 6.8 | 3.5 | 1.8 | 2.6 | 181 of 181 | 146647 | 0.0632 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 3.6 | 1.9 | 2343/672 | 0.0007 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 3 | 5.7 | 3.7 | 1678/745 | 0.0020 |  |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 3 | 3 | 8.8 | 6.2 | 3072/1451 | 0.0031 |  |
| 4-ambiguous | agent | no | complete | 1/1 | OMB M-25-21: Acceleratin p12 | 1 | 3 | 5.8 | 4.4 | 1923/863 | 0.0015 | asked: Which memo do you mean? Several OMB AI memos in the collection set 180-day deadlines, so I want to answer for the right one. missing: AI Strateg |
| 5-insufficient-evidence | agent | no | complete | 3/3 |  | 3 | 3 | 7.7 | 5.0 | 1810/1234 | 0.0019 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 2/2 | Northbridge University O p1, Northbridge University O p1 | 3 | 3 | 7.1 | 5.3 | 1704/1271 | 0.0020 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 5.7 | 2.4 | 3192/1199 | 0.0017 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 25.5 | 21.4 | 4293/1730 | 0.0028 |  |
| 8b-tool-keeps-failing | agent | no | complete | 6/6 |  | 3 | 4 | 7.8 | 5.9 | 3005/1160 | 0.0019 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 6.2 | 2.8 | 2539/1173 | 0.0009 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | no | complete | 3/3 |  | 1 | 2 | 3.3 | 2.0 | 1683/566 | 0.0012 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 4.7 | 2.8 | 2423/972 | 0.0016 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 2 | 2.5 | 1.0 | 1290/278 | 0.0011 |  |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 3 | 3 | 7.1 | 4.4 | 3095/1405 | 0.0030 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 3.8 | 2.3 | 1652/559 | 0.0012 |  |
| 1-simple-lookup | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 3.7 | 2.0 | 2150/722 | 0.0007 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 3 | 5.4 | 4.0 | 1685/856 | 0.0021 |  |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 3 | 9.3 | 6.4 | 3779/1636 | 0.0022 |  |
| 4-ambiguous | agent | no | complete | 1/1 | OMB M-25-21: Acceleratin p12 | 1 | 3 | 4.9 | 3.6 | 1946/841 | 0.0008 | asked: Which memo do you mean? Several OMB memos set 180-day deadlines, and their requirements differ. missing: AI Strateg |
| 5-insufficient-evidence | agent | no | complete | 2/2 |  | 1 | 2 | 5.0 | 3.3 | 1526/814 | 0.0006 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 3 | 3 | 5.2 | 3.9 | 2028/1024 | 0.0012 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 4.2 | 2.2 | 3210/922 | 0.0009 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 24.2 | 21.4 | 3746/1489 | 0.0019 |  |
| 8b-tool-keeps-failing | agent | no | complete | 3/3 |  | 3 | 4 | 6.1 | 4.6 | 1959/895 | 0.0013 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 3 | 5.9 | 3.9 | 2110/1001 | 0.0018 |  |
| 10-voluntary-framework | agent | no | complete | 2/2 |  | 1 | 2 | 2.8 | 1.6 | 1339/381 | 0.0004 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.4 | 2.7 | 2040/1101 | 0.0008 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 2 | 2.9 | 1.2 | 1559/387 | 0.0004 |  |
| 13-security-and-injection | agent | no | complete | 5/5 | NIST AI 600-1: AI Risk M p14 | 3 | 3 | 7.1 | 5.2 | 2624/1163 | 0.0023 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 3.8 | 2.0 | 1986/624 | 0.0006 |  |
| 1-simple-lookup | agent | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 3.8 | 1.9 | 2345/658 | 0.0007 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 3 | 6.5 | 4.7 | 1677/862 | 0.0021 |  |
| 3-multi-doc-b | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 3 | 3 | 7.8 | 5.5 | 2761/1196 | 0.0024 |  |
| 4-ambiguous | agent | no | complete | 1/1 | OMB M-25-21: Acceleratin p12 | 1 | 3 | 5.1 | 3.5 | 1935/835 | 0.0008 | asked: Several OMB memos in the collection set 180-day deadlines. Which memo do you mean? missing: AI Strateg |
| 5-insufficient-evidence | agent | no | complete | 3/3 |  | 1 | 2 | 4.6 | 3.1 | 1854/713 | 0.0006 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 3 | 8.3 | 5.0 | 2020/1193 | 0.0013 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 5.5 | 2.3 | 3203/1164 | 0.0010 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 23.3 | 20.8 | 3694/1511 | 0.0019 |  |
| 8b-tool-keeps-failing | agent | no | complete | 5/5 |  | 4 | 5 | 9.0 | 6.8 | 2552/1425 | 0.0022 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 4.5 | 2.8 | 2539/850 | 0.0008 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | no | complete | 3/3 |  | 1 | 2 | 3.8 | 2.1 | 1645/593 | 0.0006 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 7.1 | 2.7 | 1698/1212 | 0.0009 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 3.2 | 1.4 | 1682/456 | 0.0005 |  |
| 13-security-and-injection | agent | no | complete | 6/6 |  | 3 | 3 | 7.1 | 4.8 | 2754/1321 | 0.0020 | missing: attack surface, (external|third[- ]party|outside); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 3.1 | 1.6 | 1346/430 | 0.0004 |  |
