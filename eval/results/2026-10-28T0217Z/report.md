# Evaluation results, 2026-10-28T0217Z

| System | Cases passed | Mean latency (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|
| agent | 30 of 30 | 8.6 | 2.5 | 3.6 | 172 of 172 | 279876 | 0.7895 |
| baseline | 18 of 30 | 4.8 | 1.1 | 1.1 | 118 of 118 | 208438 | 0.5406 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 6/6 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 4.2 | 6054/523 | 0.0181 |  |
| 1-simple-lookup | baseline | yes | complete | 6/6 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 1 | 2.6 | 6842/407 | 0.0177 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 4 | 6.6 | 10580/638 | 0.0292 |  |
| 2-multi-doc-a | baseline | no | complete | 3/3 | NIST AI 100-1: Artificia p8 | 1 | 1 | 2.9 | 6733/352 | 0.0170 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 3 | 4 | 7.6 | 11048/917 | 0.0329 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 1 | 3.8 | 5530/445 | 0.0155 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 4 | 10.2 | 8902/1017 | 0.0294 | asked: Which memo do you mean? Several OMB memos in the collection have 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 2 | 8.4 | 12873/1076 | 0.0365 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 2/2 |  | 2 | 3 | 6.7 | 6880/399 | 0.0189 |  |
| 5-insufficient-evidence | baseline | yes | complete | 4/4 |  | 1 | 1 | 3.7 | 6859/500 | 0.0187 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 4 | 8.5 | 5203/745 | 0.0195 |  |
| 6-conflicting-sources | baseline | yes | complete | 7/7 | Northbridge University O p1, Northbridge University O p1 | 1 | 1 | 5.6 | 6332/686 | 0.0195 |  |
| 7-prompt-injection | agent | yes | complete | 4/4 | Northbridge University A p1 | 2 | 3 | 5.3 | 2749/564 | 0.0123 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 1 | 3.6 | 6451/494 | 0.0178 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 16.6 | 6772/903 | 0.0237 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 5/5 |  | 1 | 1 | 11.5 | 5843/495 | 0.0166 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 6 | 7 | 18.4 | 25146/1476 | 0.0678 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.6 | 347/130 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.0 | 8001/622 | 0.0234 |  |
| 9-supersession | baseline | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 1 | 4.2 | 6519/595 | 0.0190 |  |
| 1-simple-lookup | agent | yes | complete | 6/6 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 4.1 | 6054/557 | 0.0185 |  |
| 1-simple-lookup | baseline | yes | complete | 6/6 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 1 | 3.4 | 6842/476 | 0.0184 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 4 | 6.1 | 10580/631 | 0.0291 |  |
| 2-multi-doc-a | baseline | no | complete | 4/4 | NIST AI 100-1: Artificia p8 | 1 | 1 | 2.9 | 6733/362 | 0.0171 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 4 | 8.1 | 11050/991 | 0.0336 |  |
| 3-multi-doc-b | baseline | no | complete | 0/0 |  | 1 | 1 | 3.4 | 5530/350 | 0.0146 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 5/5 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 4 | 9.9 | 8942/1041 | 0.0298 | asked: Which memo do you mean? Several OMB memos in the collection could have 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 2 | 8.7 | 12869/1066 | 0.0364 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 1/1 |  | 1 | 2 | 3.7 | 6205/284 | 0.0161 |  |
| 5-insufficient-evidence | baseline | yes | complete | 4/4 |  | 1 | 1 | 3.7 | 6859/479 | 0.0185 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 3 | 4 | 8.8 | 5203/682 | 0.0188 |  |
| 6-conflicting-sources | baseline | yes | complete | 7/7 | Northbridge University O p1, Northbridge University O p1 | 1 | 1 | 4.8 | 6332/624 | 0.0189 |  |
| 7-prompt-injection | agent | yes | complete | 4/4 | Northbridge University A p1 | 2 | 3 | 5.7 | 2749/605 | 0.0127 |  |
| 7-prompt-injection | baseline | yes | complete | 5/5 | Northbridge University A p1 | 1 | 1 | 3.7 | 6451/497 | 0.0179 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 16.9 | 5554/1087 | 0.0231 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 1 | 11.6 | 5843/472 | 0.0164 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 5 | 6 | 14.9 | 16906/1332 | 0.0494 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.6 | 347/133 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.6 | 8001/645 | 0.0236 |  |
| 9-supersession | baseline | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 1 | 4.2 | 6519/620 | 0.0192 |  |
| 1-simple-lookup | agent | yes | complete | 7/7 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 4.5 | 6061/643 | 0.0194 |  |
| 1-simple-lookup | baseline | yes | complete | 6/6 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 1 | 2.6 | 6842/410 | 0.0178 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 4 | 6.1 | 10582/704 | 0.0298 |  |
| 2-multi-doc-a | baseline | no | complete | 3/3 | NIST AI 100-1: Artificia p8 | 1 | 1 | 3.2 | 6733/363 | 0.0171 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 4 | 8.2 | 11050/1036 | 0.0341 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 1 | 4.2 | 5530/477 | 0.0158 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 5/5 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 4 | 9.0 | 8750/950 | 0.0285 | asked: Which memo do you mean? Several OMB memos in the collection may have 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 2 | 8.5 | 12866/1013 | 0.0359 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 5.1 | 7778/395 | 0.0206 |  |
| 5-insufficient-evidence | baseline | yes | complete | 4/4 |  | 1 | 1 | 4.2 | 6859/600 | 0.0197 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 4 | 9.1 | 5203/771 | 0.0197 |  |
| 6-conflicting-sources | baseline | yes | complete | 8/8 | Northbridge University O p1, Northbridge University O p1 | 1 | 1 | 5.1 | 6332/674 | 0.0194 |  |
| 7-prompt-injection | agent | yes | complete | 4/4 | Northbridge University A p1 | 2 | 3 | 5.3 | 2749/564 | 0.0123 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 1 | 3.1 | 6451/499 | 0.0179 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 16.3 | 6772/898 | 0.0237 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 1 | 11.3 | 5843/465 | 0.0163 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 5 | 6 | 13.7 | 16888/1328 | 0.0493 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.6 | 347/133 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 3 | 4.8 | 8001/515 | 0.0223 |  |
| 9-supersession | baseline | yes | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 1 | 4.0 | 6519/569 | 0.0187 |  |
