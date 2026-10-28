# Evaluation results, 2026-10-28T211637Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 43 of 45 | 7.7 | 5.2 | 1.8 | 3.4 | 194 of 194 | 155786 | 0.0843 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.9 | 3.3 | 2056/702 | 0.0018 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 5.2 | 3.8 | 1682/916 | 0.0023 |  |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 10.0 | 6.9 | 4040/1967 | 0.0024 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.7 | 6.1 | 2261/1429 | 0.0020 | asked: Which memo do you mean? Several OMB AI memos are in the collection, and I want to check the correct one for the 180-day requirement. |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 3 | 4 | 7.1 | 5.6 | 1319/875 | 0.0030 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 4 | 8.9 | 7.3 | 2279/1352 | 0.0019 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 1 | 3 | 5.6 | 4.0 | 1284/658 | 0.0008 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.5 | 12.6 | 3570/1443 | 0.0018 |  |
| 8b-tool-keeps-failing | agent | no | complete | 4/4 |  | 3 | 5 | 7.2 | 5.3 | 2640/1408 | 0.0020 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | yes | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 3 | 7.1 | 5.2 | 2323/1153 | 0.0025 |  |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p7 | 2 | 3 | 6.2 | 4.8 | 1701/981 | 0.0018 |  |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.5 | 4.7 | 2087/1177 | 0.0024 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.7 | 4.4 | 1720/638 | 0.0015 |  |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.9 | 6.2 | 4528/1986 | 0.0030 |  |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 6.5 | 4.4 | 1579/717 | 0.0014 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.7 | 2.7 | 2004/657 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 6.0 | 4.4 | 1646/1068 | 0.0022 |  |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 8.2 | 6.1 | 3062/1567 | 0.0021 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 8.6 | 7.1 | 1868/1516 | 0.0020 | asked: Several documents set 180-day deadlines for agencies. Which memo do you mean? |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 5.8 | 4.6 | 1276/774 | 0.0021 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 2 | 4 | 10.1 | 8.0 | 1990/1331 | 0.0016 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 2 | 3 | 8.4 | 4.7 | 3184/1719 | 0.0015 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 17.6 | 14.5 | 4084/1995 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 12.0 | 9.0 | 3508/2358 | 0.0032 | recovered. |
| 9-supersession | agent | no | complete | 2/2 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 4 | 7.7 | 6.2 | 1323/1113 | 0.0017 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 1 | 3 | 4.8 | 3.6 | 1321/700 | 0.0011 |  |
| 11-acquisition-supersession | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.1 | 4.6 | 1425/1011 | 0.0022 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.1 | 2.6 | 1732/592 | 0.0006 |  |
| 13-security-and-injection | agent | yes | complete | 5/5 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.1 | 5.2 | 2434/1359 | 0.0024 |  |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.5 | 3.3 | 1554/666 | 0.0006 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 3.9 | 2.3 | 1646/474 | 0.0005 |  |
| 2-multi-doc-a | agent | yes | complete | 4/4 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 7.6 | 4.3 | 1943/1070 | 0.0023 |  |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 2 | 3 | 7.7 | 5.2 | 3144/1660 | 0.0026 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 8.2 | 6.2 | 2237/1459 | 0.0021 | asked: Several documents in the collection set 180-day requirements for agencies. Which memo do you mean? |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 4 | 8.9 | 6.9 | 1673/864 | 0.0022 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 2 | 4 | 8.4 | 6.5 | 1987/1217 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 1/1 | Northbridge University A p1 | 1 | 3 | 4.1 | 3.3 | 966/571 | 0.0006 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.8 | 12.3 | 3549/1425 | 0.0012 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 6 | 8 | 13.0 | 10.8 | 3727/2565 | 0.0038 | recovered. |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 3 | 8.1 | 5.6 | 2841/1469 | 0.0026 |  |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p7 | 2 | 3 | 6.7 | 4.3 | 1603/847 | 0.0017 |  |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.7 | 5.1 | 1976/1261 | 0.0024 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 3.7 | 2.4 | 1694/575 | 0.0006 |  |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.3 | 6.5 | 3917/1879 | 0.0028 |  |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.7 | 3.0 | 1578/661 | 0.0006 |  |
