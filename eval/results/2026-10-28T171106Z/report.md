# Evaluation results, 2026-10-28T171106Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 40 of 45 | 10.0 | 5.6 | 1.4 | 3.3 | 218 of 218 | 136404 | 1.1359 |
| baseline | 21 of 45 | 7.4 | 4.0 | 1.1 | 2.0 | 164 of 164 | 407075 | 1.0661 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 15.9 | 9.6 | 2198/886 | 0.0358 |  |
| 1-simple-lookup | baseline | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 5.6 | 2.4 | 8774/662 | 0.0242 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.6 | 6.6 | 1654/816 | 0.0307 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 2 | 4.1 | 1.9 | 7969/337 | 0.0193 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 11.0 | 7.6 | 2833/1312 | 0.0380 |  |
| 3-multi-doc-b | baseline | no | complete | 0/0 |  | 1 | 1 | 5.1 | 5.1 | 5560/374 | 0.0149 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 12.6 | 7.7 | 1935/1195 | 0.0353 | asked: Which memo do you mean? Several of the OMB memos set 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 4/4 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 13.7 | 8.0 | 17554/1775 | 0.0529 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 1 | 3 | 11.0 | 4.8 | 1505/656 | 0.0238 |  |
| 5-insufficient-evidence | baseline | no | complete | 4/4 |  | 1 | 2 | 8.6 | 4.1 | 8764/810 | 0.0256 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 7.5 | 5.7 | 1583/699 | 0.0196 |  |
| 6-conflicting-sources | baseline | yes | complete | 7/7 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 9.3 | 6.0 | 9504/1036 | 0.0294 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 10.5 | 4.4 | 2563/884 | 0.0205 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 6.8 | 4.0 | 9055/875 | 0.0269 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 19.9 | 15.4 | 3573/1577 | 0.0379 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 16.0 | 11.7 | 7460/695 | 0.0219 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 17.7 | 12.7 | 3203/1812 | 0.0470 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 2.9 | 2.9 | 377/124 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 8.3 | 5.3 | 1818/839 | 0.0319 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 8.1 | 4.1 | 9065/799 | 0.0261 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p47, NIST AI 100-1: Artificia p7 | 1 | 3 | 7.0 | 3.9 | 1384/608 | 0.0225 |  |
| 10-voluntary-framework | baseline | no | complete | 4/4 |  | 1 | 2 | 6.1 | 4.1 | 8096/603 | 0.0222 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 1 | 3 | 7.3 | 4.7 | 1542/655 | 0.0263 |  |
| 11-acquisition-supersession | baseline | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.6 | 3.5 | 9418/684 | 0.0257 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.1 | 2.2 | 1063/367 | 0.0176 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 3.9 | 2.1 | 7836/410 | 0.0198 |  |
| 13-security-and-injection | agent | yes | complete | 13/13 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 12.9 | 8.7 | 4301/1871 | 0.0479 |  |
| 13-security-and-injection | baseline | no | complete | 4/4 |  | 1 | 2 | 8.5 | 5.8 | 7912/747 | 0.0233 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 1/1 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.9 | 3.0 | 870/268 | 0.0165 |  |
| 14-contract-start | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 4.8 | 2.1 | 7773/512 | 0.0207 |  |
| 1-simple-lookup | agent | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 9.0 | 5.6 | 2191/895 | 0.0142 |  |
| 1-simple-lookup | baseline | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 8.4 | 2.6 | 8818/665 | 0.0243 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 9.5 | 5.7 | 1420/688 | 0.0256 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 2 | 4.4 | 1.8 | 7976/389 | 0.0198 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 9.5 | 6.3 | 2806/1322 | 0.0200 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 2 | 5.9 | 4.1 | 7029/643 | 0.0205 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.7 | 5.6 | 1954/1006 | 0.0315 | asked: Which memo do you mean? Several OMB memos in the collection set deadlines for agencies. |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 12.9 | 7.1 | 17373/1600 | 0.0508 | missing: AI Strateg |
| 5-insufficient-evidence | agent | no | complete | 2/2 |  | 1 | 3 | 5.5 | 4.2 | 1219/509 | 0.0195 | failed check: gold_page_cited |
| 5-insufficient-evidence | baseline | no | complete | 5/5 |  | 1 | 2 | 8.4 | 4.1 | 8959/786 | 0.0258 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 7.9 | 5.4 | 1913/833 | 0.0129 |  |
| 6-conflicting-sources | baseline | yes | complete | 8/8 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 8.8 | 5.8 | 9120/1077 | 0.0290 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 8.2 | 4.5 | 2557/921 | 0.0150 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 7.2 | 4.4 | 9283/921 | 0.0278 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 21.4 | 16.6 | 3579/1662 | 0.0248 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 14.6 | 12.1 | 7498/760 | 0.0226 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 21.6 | 14.2 | 2994/1908 | 0.0522 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.7 | 1.6 | 377/117 | 0.0019 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 7.3 | 5.4 | 1714/859 | 0.0261 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 7.2 | 4.8 | 9203/906 | 0.0275 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p47 | 1 | 3 | 5.6 | 3.8 | 1469/634 | 0.0211 |  |
| 10-voluntary-framework | baseline | no | complete | 3/3 |  | 1 | 2 | 9.2 | 4.0 | 7797/560 | 0.0212 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p1 | 1 | 3 | 6.1 | 4.1 | 1222/527 | 0.0226 |  |
| 11-acquisition-supersession | baseline | yes | complete | 6/6 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.5 | 3.7 | 9707/785 | 0.0273 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.1 | 2.3 | 1063/367 | 0.0067 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 4.1 | 2.3 | 7848/407 | 0.0198 |  |
| 13-security-and-injection | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 16.7 | 8.6 | 3613/1698 | 0.0437 |  |
| 13-security-and-injection | baseline | no | complete | 4/4 |  | 1 | 2 | 10.9 | 5.4 | 7651/736 | 0.0227 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 1/1 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.9 | 3.3 | 1100/374 | 0.0150 |  |
| 14-contract-start | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 7.0 | 2.1 | 7801/518 | 0.0208 |  |
| 1-simple-lookup | agent | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 7.0 | 4.3 | 2198/904 | 0.0143 |  |
| 1-simple-lookup | baseline | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 5.0 | 2.6 | 9016/733 | 0.0254 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.9 | 6.2 | 1630/786 | 0.0123 |  |
| 2-multi-doc-a | baseline | no | complete | 1/1 | NIST AI 100-1: Artificia p8 | 1 | 2 | 6.4 | 1.7 | 7704/270 | 0.0181 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 10.2 | 6.2 | 2754/1297 | 0.0358 |  |
| 3-multi-doc-b | baseline | no | complete | 0/0 |  | 1 | 1 | 3.4 | 3.4 | 5560/333 | 0.0144 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 10.9 | 7.7 | 1939/1082 | 0.0322 | asked: Which memo do you mean? Several OMB memos in the collection include 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 4/4 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 12.0 | 7.1 | 17331/1703 | 0.0517 | missing: AI Strateg |
| 5-insufficient-evidence | agent | no | complete | 1/1 |  | 1 | 3 | 6.9 | 3.7 | 898/380 | 0.0169 | missing: 180; failed check: gold_page_cited |
| 5-insufficient-evidence | baseline | no | complete | 4/4 |  | 1 | 2 | 7.5 | 4.8 | 8732/775 | 0.0252 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 8.2 | 6.1 | 1913/837 | 0.0130 |  |
| 6-conflicting-sources | baseline | yes | complete | 8/8 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 7.5 | 4.8 | 9380/1016 | 0.0289 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 8.6 | 5.8 | 2558/900 | 0.0148 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 9.6 | 5.2 | 9054/839 | 0.0265 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 20.2 | 15.9 | 3746/1597 | 0.0245 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 14.7 | 12.7 | 7474/734 | 0.0223 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 16.0 | 11.7 | 2981/1730 | 0.0421 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 3.2 | 3.2 | 377/123 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 3 | 8.3 | 4.8 | 1775/726 | 0.0285 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 7.3 | 4.6 | 9218/915 | 0.0276 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 4 | 7.4 | 5.5 | 1160/627 | 0.0246 |  |
| 10-voluntary-framework | baseline | no | complete | 4/4 |  | 1 | 2 | 5.8 | 3.3 | 8094/612 | 0.0223 | missing: voluntary; failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 1 | 3 | 6.9 | 4.7 | 1788/712 | 0.0118 |  |
| 11-acquisition-supersession | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.3 | 3.5 | 8790/452 | 0.0221 |  |
| 12-core-cross-cutting | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p25 | 1 | 3 | 6.0 | 2.2 | 1057/364 | 0.0066 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 4.3 | 2.3 | 7848/407 | 0.0198 |  |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 13.0 | 7.8 | 3407/1660 | 0.0405 |  |
| 13-security-and-injection | baseline | no | complete | 3/3 |  | 1 | 2 | 7.4 | 3.9 | 7375/598 | 0.0207 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 6.4 | 3.7 | 1116/395 | 0.0158 |  |
| 14-contract-start | baseline | yes | complete | 4/4 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 6.7 | 3.8 | 8079/663 | 0.0228 |  |
