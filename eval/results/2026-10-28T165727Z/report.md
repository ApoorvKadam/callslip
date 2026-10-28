# Evaluation results, 2026-10-28T165727Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 43 of 45 | 8.6 | 5.5 | 1.8 | 3.4 | 206 of 206 | 150138 | 0.0880 |
| baseline | 21 of 45 | 7.7 | 5.2 | 1.1 | 2.1 | 121 of 121 | 414588 | 0.0633 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 5.6 | 3.9 | 1469/604 | 0.0011 |  |
| 1-simple-lookup | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 4.6 | 3.0 | 8578/816 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 7.8 | 5.8 | 1639/1221 | 0.0024 |  |
| 2-multi-doc-a | baseline | no | complete | 3/3 | NIST AI 100-1: Artificia p8 | 1 | 2 | 8.1 | 6.3 | 8143/1094 | 0.0014 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 13.8 | 10.8 | 3406/2269 | 0.0026 |  |
| 3-multi-doc-b | baseline | no | complete | 2/2 |  | 1 | 2 | 6.8 | 5.3 | 6831/1176 | 0.0013 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.4 | 5.4 | 2223/1431 | 0.0020 | asked: Several documents in the collection are OMB memos on AI. Which one do you mean? |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 19.5 | 15.0 | 15957/3311 | 0.0032 | missing: AI Strateg, compliance plan |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 3 | 4 | 9.9 | 8.7 | 1185/1032 | 0.0030 |  |
| 5-insufficient-evidence | baseline | no | complete | 2/2 |  | 1 | 2 | 6.5 | 4.9 | 8255/1120 | 0.0014 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 8.3 | 6.5 | 2124/1428 | 0.0017 |  |
| 6-conflicting-sources | baseline | yes | complete | 6/6 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 6.9 | 5.2 | 8543/1384 | 0.0015 |  |
| 7-prompt-injection | agent | yes | complete | 4/4 | Northbridge University A p1 | 2 | 3 | 6.4 | 4.0 | 2734/1406 | 0.0014 |  |
| 7-prompt-injection | baseline | yes | complete | 2/2 | Northbridge University A p1 | 1 | 2 | 6.8 | 5.2 | 7622/1195 | 0.0014 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 5/5 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 15.8 | 13.4 | 1926/1255 | 0.0016 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 15.6 | 13.7 | 7457/1112 | 0.0013 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 14.5 | 12.3 | 2490/2465 | 0.0034 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.2 | 1.2 | 377/121 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 4 | 8.8 | 6.4 | 2177/1414 | 0.0027 |  |
| 9-supersession | baseline | no | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 7.3 | 5.9 | 7996/1461 | 0.0015 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p7 | 2 | 3 | 5.8 | 3.9 | 1594/902 | 0.0022 |  |
| 10-voluntary-framework | baseline | no | complete | 3/3 |  | 1 | 2 | 4.9 | 3.5 | 7773/822 | 0.0012 | missing: voluntary; failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 6.8 | 5.2 | 1695/1226 | 0.0023 |  |
| 11-acquisition-supersession | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.1 | 4.6 | 8487/1079 | 0.0014 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.7 | 2.9 | 1467/601 | 0.0014 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 6.8 | 3.6 | 7843/859 | 0.0012 |  |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.5 | 5.5 | 2503/1571 | 0.0026 |  |
| 13-security-and-injection | baseline | no | complete | 1/1 |  | 1 | 2 | 9.7 | 5.5 | 6519/884 | 0.0011 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 2 | 3 | 7.6 | 4.7 | 1368/845 | 0.0022 |  |
| 14-contract-start | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 5.6 | 4.6 | 7376/902 | 0.0012 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 6.0 | 4.1 | 1730/686 | 0.0011 |  |
| 1-simple-lookup | baseline | yes | complete | 2/2 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26 | 1 | 2 | 6.3 | 4.5 | 8025/960 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.8 | 6.3 | 1442/1242 | 0.0023 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 2 | 8.3 | 7.2 | 7917/1052 | 0.0013 | missing: misinformation, climate change, valid and reliable; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 9.2 | 7.0 | 2680/1945 | 0.0021 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 2 | 8.4 | 6.5 | 7054/1500 | 0.0014 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.6 | 5.5 | 1951/1241 | 0.0018 | asked: Several of the documents are OMB memos, so I need to know which one you mean by "the memo" before I look up the 180-day requirement. Which one? |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 16.7 | 12.9 | 16212/3223 | 0.0032 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 3 | 4 | 9.5 | 7.8 | 1162/918 | 0.0029 |  |
| 5-insufficient-evidence | baseline | no | complete | 4/4 |  | 1 | 2 | 7.5 | 5.2 | 9278/1369 | 0.0016 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 9.1 | 7.1 | 1870/1357 | 0.0013 |  |
| 6-conflicting-sources | baseline | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 6.3 | 4.6 | 7999/1136 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 7.3 | 3.8 | 2609/1504 | 0.0013 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 9.7 | 7.6 | 9081/2072 | 0.0019 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 16.4 | 13.2 | 3737/1843 | 0.0021 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 3/3 |  | 1 | 2 | 15.7 | 13.8 | 7274/1239 | 0.0014 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 6 | 8 | 16.0 | 12.9 | 3231/2852 | 0.0042 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.4 | 1.4 | 377/137 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.6 | 5.3 | 1725/1142 | 0.0024 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 6.8 | 4.8 | 8913/1265 | 0.0015 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p7 | 2 | 3 | 5.5 | 3.8 | 1439/1014 | 0.0017 |  |
| 10-voluntary-framework | baseline | no | complete | 2/2 |  | 1 | 2 | 4.3 | 2.8 | 7502/576 | 0.0010 | missing: voluntary; failed check: gold_page_cited; failed check: says_evidence_missing |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 1 | 3 | 6.8 | 4.2 | 1764/1080 | 0.0015 |  |
| 11-acquisition-supersession | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 8.5 | 6.1 | 8945/1409 | 0.0016 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 3.8 | 2.7 | 1134/438 | 0.0004 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 6.5 | 4.5 | 7895/1131 | 0.0014 |  |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 10.8 | 5.7 | 2599/2167 | 0.0025 |  |
| 13-security-and-injection | baseline | no | complete | 2/2 |  | 1 | 2 | 7.6 | 6.2 | 7149/1285 | 0.0014 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 5.3 | 3.7 | 1345/577 | 0.0013 |  |
| 14-contract-start | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 4.3 | 3.1 | 7384/721 | 0.0011 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.5 | 3.2 | 1749/704 | 0.0006 |  |
| 1-simple-lookup | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 4.2 | 2.3 | 8527/658 | 0.0012 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 6.7 | 5.2 | 1462/1032 | 0.0022 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 2 | 8.8 | 7.1 | 8010/1396 | 0.0015 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 10.2 | 7.5 | 2972/2090 | 0.0023 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 2 | 7.5 | 5.5 | 7084/1277 | 0.0014 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.5 | 5.5 | 1936/1343 | 0.0018 | asked: Several OMB memos in the collection could be "the memo." Which one do you mean, so I can check its 180-day requirements? |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 14.4 | 11.5 | 16186/2864 | 0.0031 | missing: AI Strateg; failed check: asked_for_clarification |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 7.9 | 6.3 | 1475/972 | 0.0022 |  |
| 5-insufficient-evidence | baseline | no | complete | 3/3 |  | 1 | 2 | 7.8 | 5.8 | 8910/1263 | 0.0015 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 8.4 | 6.6 | 1886/1199 | 0.0012 |  |
| 6-conflicting-sources | baseline | yes | complete | 5/5 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 8.5 | 4.8 | 8638/1741 | 0.0017 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 2 | 3 | 7.4 | 4.9 | 1128/966 | 0.0009 |  |
| 7-prompt-injection | baseline | yes | complete | 2/2 | Northbridge University A p1 | 1 | 2 | 5.0 | 3.9 | 7641/961 | 0.0013 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 17.0 | 13.8 | 4268/1959 | 0.0015 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 14.7 | 13.3 | 7427/1133 | 0.0013 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | no | complete | 5/5 |  | 4 | 6 | 11.8 | 8.7 | 2060/1644 | 0.0023 | neither. failed check: recovered_or_reported_incomplete |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.4 | 1.4 | 377/142 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 7/7 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 4 | 11.9 | 9.3 | 2498/1561 | 0.0027 |  |
| 9-supersession | baseline | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 6.7 | 4.9 | 8681/1259 | 0.0015 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 1 | 3 | 4.4 | 3.3 | 1153/679 | 0.0011 |  |
| 10-voluntary-framework | baseline | no | complete | 3/3 |  | 1 | 2 | 4.7 | 3.4 | 7792/749 | 0.0011 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 7.2 | 5.3 | 1996/1381 | 0.0024 |  |
| 11-acquisition-supersession | baseline | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 7.3 | 5.6 | 9103/1260 | 0.0015 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.7 | 3.5 | 1690/717 | 0.0014 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 7.7 | 5.8 | 7872/915 | 0.0013 |  |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.1 | 6.3 | 3410/2099 | 0.0026 |  |
| 13-security-and-injection | baseline | no | complete | 3/3 |  | 1 | 2 | 9.6 | 6.9 | 7546/1900 | 0.0017 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 6.4 | 4.5 | 1362/653 | 0.0013 |  |
| 14-contract-start | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 4.6 | 3.6 | 7356/747 | 0.0011 |  |
