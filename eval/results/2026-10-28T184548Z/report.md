# Evaluation results, 2026-10-28T184548Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 36 of 45 | 6.6 | 4.3 | 1.6 | 3.2 | 143 of 143 | 122818 | 0.0691 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.0 | 2.3 | 1713/607 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.7 | 7.1 | 1663/1146 | 0.0023 |  |
| 3-multi-doc-b | agent | yes | complete | 4/4 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 6.6 | 5.1 | 2160/1333 | 0.0019 |  |
| 4-ambiguous | agent | no | complete | 2/2 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 6.4 | 4.6 | 1812/1059 | 0.0018 | asked: Several documents in the collection are OMB memos. Which one do you mean by "the memo"? missing: compliance plan |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 4 | 6.4 | 4.6 | 1368/766 | 0.0021 |  |
| 6-conflicting-sources | agent | yes | complete | 2/2 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 6.0 | 4.4 | 1716/1027 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 1/1 | Northbridge University A p1 | 1 | 3 | 4.7 | 3.2 | 983/542 | 0.0007 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.5 | 12.8 | 3225/1322 | 0.0017 |  |
| 8b-tool-keeps-failing | agent | no | complete | 0/0 |  | 2 | 3 | 3.7 | 3.7 | 8/336 | 0.0003 | neither. failed check: recovered_or_reported_incomplete |
| 9-supersession | agent | no | complete | 2/2 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 6.1 | 4.9 | 1337/801 | 0.0015 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 1/1 | NIST AI 100-1: Artificia p7 | 2 | 3 | 4.8 | 2.9 | 978/591 | 0.0016 |  |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.2 | 4.3 | 2043/1069 | 0.0025 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 3.8 | 2.6 | 1254/366 | 0.0013 |  |
| 13-security-and-injection | agent | no | complete | 4/4 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 6.5 | 4.7 | 2208/1242 | 0.0021 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.2 | 2.7 | 1264/462 | 0.0013 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 3.8 | 2.4 | 1683/561 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.2 | 6.3 | 1659/1171 | 0.0023 |  |
| 3-multi-doc-b | agent | yes | complete | 4/4 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 5.7 | 4.2 | 1903/1033 | 0.0016 |  |
| 4-ambiguous | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 6.8 | 4.9 | 1897/1123 | 0.0017 | asked: Which memo do you mean? Several OMB AI memos in the collection could contain a 180-day requirement. |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.4 | 4.2 | 1663/819 | 0.0021 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 6.0 | 4.4 | 2002/1120 | 0.0012 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 1 | 3 | 6.0 | 4.2 | 1338/784 | 0.0006 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 16.0 | 13.5 | 3217/1473 | 0.0012 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 5/5 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 11.3 | 9.7 | 2551/1917 | 0.0026 | recovered. |
| 9-supersession | agent | no | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 7.7 | 4.8 | 1712/1193 | 0.0017 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 4.2 | 3.0 | 1284/673 | 0.0015 |  |
| 11-acquisition-supersession | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p1 | 1 | 3 | 5.5 | 3.8 | 1404/733 | 0.0013 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 3.3 | 2.0 | 1239/358 | 0.0012 |  |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 8.1 | 5.9 | 3048/1571 | 0.0021 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.4 | 3.0 | 1583/566 | 0.0013 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 3.5 | 2.3 | 1689/568 | 0.0010 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 6.5 | 4.8 | 1661/779 | 0.0021 |  |
| 3-multi-doc-b | agent | no | complete | 5/5 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 6.4 | 4.9 | 2260/1260 | 0.0017 | missing: confident |
| 4-ambiguous | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 6.7 | 5.3 | 1865/1155 | 0.0017 | asked: Which memo do you mean? Several OMB AI memos are in the collection, and each may set its own 180-day deadlines. |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 5.6 | 4.7 | 1278/743 | 0.0021 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 5.9 | 4.1 | 1659/935 | 0.0007 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 1 | 3 | 5.3 | 3.6 | 1284/677 | 0.0005 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.6 | 12.9 | 3801/1531 | 0.0013 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 13.7 | 11.3 | 3130/1969 | 0.0028 | recovered. |
| 9-supersession | agent | no | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 6.6 | 4.0 | 1670/1166 | 0.0017 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 1/1 | NIST AI 100-1: Artificia p7 | 2 | 3 | 5.0 | 3.1 | 996/626 | 0.0015 |  |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 5.9 | 4.6 | 2015/1087 | 0.0023 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.1 | 2.2 | 1647/534 | 0.0006 |  |
| 13-security-and-injection | agent | no | complete | 4/4 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 5.9 | 3.8 | 1997/1033 | 0.0022 | missing: (external|third[- ]party|outside) |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.6 | 3.2 | 1561/563 | 0.0012 |  |
