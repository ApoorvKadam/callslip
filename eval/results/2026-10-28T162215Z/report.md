# Evaluation results, 2026-10-28T162215Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 39 of 45 | 8.9 | 6.3 | 2.0 | 3.4 | 215 of 215 | 158236 | 0.0984 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 5.0 | 3.3 | 1665/835 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 7.5 | 5.6 | 1709/1289 | 0.0024 |  |
| 3-multi-doc-b | agent | no | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 9.1 | 6.5 | 2745/1896 | 0.0023 | missing: confident |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 9.2 | 7.7 | 1511/1627 | 0.0019 | asked: Several documents in the collection are OMB memoranda. Which one do you mean by "the memo"? |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.4 | 4.8 | 1545/1157 | 0.0024 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 8.9 | 7.3 | 1687/1396 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 1 | 3 | 5.8 | 4.5 | 1340/756 | 0.0009 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 17.3 | 14.4 | 3928/1914 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 6 | 6 | 15.3 | 12.8 | 2187/2848 | 0.0036 | recovered. |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 4 | 9.3 | 5.8 | 1791/1322 | 0.0026 |  |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 4.8 | 3.7 | 1155/837 | 0.0021 |  |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 12.2 | 9.9 | 2032/2220 | 0.0030 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.8 | 4.1 | 1445/646 | 0.0015 |  |
| 13-security-and-injection | agent | no | complete | 11/11 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.9 | 7.0 | 3426/2188 | 0.0030 | missing: attack surface, (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 5.4 | 3.6 | 1366/741 | 0.0014 |  |
| 1-simple-lookup | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 6.0 | 4.4 | 1693/938 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 7.1 | 5.5 | 1663/1314 | 0.0024 |  |
| 3-multi-doc-b | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 9.1 | 6.7 | 2804/2045 | 0.0024 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 4 | 5 | 10.4 | 8.1 | 1955/1875 | 0.0029 | asked: Several documents in the collection set 180-day requirements for agencies. Which memo do you mean? |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.8 | 5.1 | 1220/1011 | 0.0022 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 9.0 | 6.9 | 2236/1631 | 0.0020 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 2 | 3 | 7.2 | 5.0 | 2613/1441 | 0.0013 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 18.2 | 15.4 | 3088/2069 | 0.0029 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 6 | 8 | 14.5 | 11.4 | 3772/2704 | 0.0043 | recovered. |
| 9-supersession | agent | yes | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 9.6 | 7.8 | 2075/1694 | 0.0032 |  |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 6.3 | 3.6 | 1114/759 | 0.0020 |  |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 8.1 | 6.3 | 1675/1398 | 0.0024 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.5 | 3.2 | 1430/669 | 0.0006 |  |
| 13-security-and-injection | agent | no | complete | 8/8 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.1 | 6.6 | 2680/1811 | 0.0026 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 2 | 3 | 7.4 | 5.2 | 1357/993 | 0.0021 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.1 | 2.4 | 1742/696 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.6 | 6.8 | 1739/1620 | 0.0025 |  |
| 3-multi-doc-b | agent | no | complete | 6/6 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 8.7 | 6.8 | 2155/1812 | 0.0022 | missing: confident |
| 4-ambiguous | agent | no | complete | 1/1 | OMB M-25-21: Acceleratin p12 | 1 | 4 | 6.9 | 5.7 | 1350/1043 | 0.0016 | asked: Several documents are OMB memoranda. Which one do you mean by "the memo" for the 180-day requirement? missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.7 | 5.4 | 1505/1027 | 0.0022 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 10.3 | 7.4 | 1674/1375 | 0.0015 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 7.8 | 4.4 | 2581/1596 | 0.0011 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 14/14 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 19.7 | 15.5 | 4364/2359 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 6 | 7 | 14.9 | 12.0 | 2507/2710 | 0.0041 | recovered. |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 10.3 | 7.5 | 2834/1743 | 0.0035 |  |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 5.4 | 4.1 | 1108/793 | 0.0020 |  |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 8.8 | 6.9 | 2087/1519 | 0.0026 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.4 | 2.7 | 1390/606 | 0.0006 |  |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.5 | 5.2 | 2472/1632 | 0.0025 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 2 | 3 | 9.6 | 7.6 | 1776/1490 | 0.0025 |  |
