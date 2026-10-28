# Evaluation results, 2026-10-28T043802Z

| System | Cases passed | Mean latency (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|
| agent | 30 of 30 | 8.3 | 2.7 | 3.8 | 167 of 167 | 593594 | 0.0772 |
| baseline | 11 of 30 | 7.5 | 1.1 | 1.1 | 85 of 85 | 235888 | 0.0403 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 4.7 | 6019/616 | 0.0014 |  |
| 1-simple-lookup | baseline | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 1 | 4.7 | 6879/979 | 0.0012 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 4 | 6.7 | 19523/1004 | 0.0025 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 1 | 6.0 | 6770/1145 | 0.0013 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 3 | 4 | 9.8 | 18182/1858 | 0.0028 |  |
| 3-multi-doc-b | baseline | no | complete | 2/2 |  | 1 | 1 | 8.4 | 5567/1400 | 0.0013 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 5/5 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 3 | 5 | 9.1 | 31393/1782 | 0.0041 | asked: Several documents in the collection set 180-day deadlines for agencies, so I want to make sure I pull the right one. Which memo do you mean? |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 2 | 19.7 | 12918/4187 | 0.0034 | missing: AI Strateg; failed check: asked_for_clarification |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.5 | 16817/1036 | 0.0023 |  |
| 5-insufficient-evidence | baseline | no | complete | 3/3 |  | 1 | 1 | 5.1 | 6896/1131 | 0.0013 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 6.7 | 12681/1122 | 0.0019 |  |
| 6-conflicting-sources | baseline | no | complete | 0/0 |  | 1 | 1 | 6.1 | 6369/1169 | 0.0012 | failed check: gold_page_cited; failed check: documents_covered |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 2 | 3 | 4.8 | 2791/855 | 0.0008 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 1 | 5.0 | 6488/1149 | 0.0012 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 1 | 2 | 14.6 | 5206/1290 | 0.0012 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 3/3 |  | 1 | 1 | 13.6 | 5880/933 | 0.0010 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p11 | 6 | 7 | 12.8 | 31773/1873 | 0.0043 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.5 | 377/152 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 6.8 | 33025/1005 | 0.0039 |  |
| 9-supersession | baseline | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 1 | 7.6 | 6556/1673 | 0.0015 | failed check: key_pages_cited |
| 1-simple-lookup | agent | yes | complete | 6/6 | NIST AI 100-1: Artificia p25 | 1 | 2 | 4.1 | 6019/684 | 0.0010 |  |
| 1-simple-lookup | baseline | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 1 | 5.3 | 6879/1223 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 4 | 6.3 | 19523/938 | 0.0025 |  |
| 2-multi-doc-a | baseline | no | complete | 4/4 | NIST AI 100-1: Artificia p8 | 1 | 1 | 5.6 | 6770/1170 | 0.0013 | missing: misinformation, climate change, valid and reliable; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 4 | 5 | 13.6 | 34333/2390 | 0.0047 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 1 | 6.7 | 5567/1408 | 0.0013 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 4 | 7.2 | 9368/1325 | 0.0017 | asked: Which memo do you mean? Several documents in the collection are OMB memos, and more than one may set 180-day deadlines. Please tell me which one to check. |
| 4-ambiguous | baseline | no | complete | 4/4 | OMB M-25-21: Acceleratin p12 | 2 | 2 | 13.7 | 12915/2985 | 0.0028 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p5 | 3 | 4 | 7.0 | 34387/1058 | 0.0041 |  |
| 5-insufficient-evidence | baseline | no | complete | 3/3 |  | 1 | 1 | 6.0 | 6896/1312 | 0.0014 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 6.9 | 12623/1226 | 0.0019 |  |
| 6-conflicting-sources | baseline | yes | complete | 2/2 | Northbridge University O p1, Northbridge University O p1 | 1 | 1 | 5.9 | 6369/1359 | 0.0013 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 5.8 | 5626/1162 | 0.0012 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 1 | 5.7 | 6488/1319 | 0.0013 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 13/13 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 16.6 | 7577/1526 | 0.0016 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 3/3 |  | 1 | 1 | 13.9 | 5880/1108 | 0.0011 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 7 | 8 | 12.7 | 49904/2170 | 0.0062 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.1 | 377/119 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 4 | 5 | 9.8 | 36500/1322 | 0.0044 |  |
| 9-supersession | baseline | no | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 1 | 6.1 | 6556/1393 | 0.0014 | failed check: key_pages_cited |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 3.0 | 6019/489 | 0.0009 |  |
| 1-simple-lookup | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 1 | 3.8 | 6879/784 | 0.0011 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 4 | 5.4 | 19536/864 | 0.0025 |  |
| 2-multi-doc-a | baseline | no | complete | 4/4 | NIST AI 100-1: Artificia p8 | 1 | 1 | 6.7 | 6770/986 | 0.0012 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 4 | 7.3 | 17389/1354 | 0.0025 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 1 | 7.9 | 5567/1673 | 0.0014 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 4 | 6.3 | 9231/1212 | 0.0016 | asked: Several documents in the collection are memos directed at agencies. Which one do you mean? |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 2 | 15.3 | 12926/3380 | 0.0030 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p5 | 3 | 4 | 6.8 | 34979/1082 | 0.0041 |  |
| 5-insufficient-evidence | baseline | no | complete | 0/0 |  | 1 | 1 | 4.2 | 6896/869 | 0.0011 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 4 | 8.2 | 19290/1336 | 0.0027 |  |
| 6-conflicting-sources | baseline | yes | complete | 6/6 | Northbridge University O p1, Northbridge University O p1 | 1 | 1 | 10.2 | 6369/2307 | 0.0018 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 4.6 | 5824/865 | 0.0011 |  |
| 7-prompt-injection | baseline | yes | complete | 4/4 | Northbridge University A p1 | 1 | 1 | 8.0 | 6488/1924 | 0.0016 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 13/13 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 15.5 | 7577/1294 | 0.0015 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 6/6 |  | 1 | 1 | 14.9 | 5880/1291 | 0.0012 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 5 | 6 | 9.8 | 16059/1492 | 0.0025 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.1 | 377/121 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 8.3 | 26961/1229 | 0.0034 |  |
| 9-supersession | baseline | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 1 | 5.2 | 6556/1134 | 0.0012 | failed check: key_pages_cited |
