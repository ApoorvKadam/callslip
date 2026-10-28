# Evaluation results, 2026-10-28T165727Z

| System | Cases passed | Completed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|---|
| agent | 43 of 45 | 45 of 45 | 8.6 | 5.5 | 1.8 | 3.4 | 206 of 206 | 150138 | 0.0880 |
| baseline | 21 of 45 | 42 of 45 | 7.7 | 5.2 | 1.1 | 2.1 | 121 of 121 | 414588 | 0.0633 |

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

## Each case: expected and actual (first repeat)

### 1-simple-lookup

Question: What are the four functions of the NIST AI RMF Core?

Expected: Simple lookup (`answer`); required: GOVERN, MAP, MEASURE, MANAGE; gold pages: NIST AI 100-1 p. 8, 25, 26.

- **agent**: pass, complete, 1 tool calls, 3.9 s to answer, 2073 tokens, cited NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8.
  > The four functions of the AI RMF Core are GOVERN, MAP, MEASURE, and MANAGE. The AI RMF Core provides outcomes and actions that enable dialogue, understanding, and activities to manage AI risks and responsibly develop trustworthy AI systems. While GOVERN applies to all stages of organizations' AI risk management processes and procedures, the MAP, MEASURE, and MANAGE functions can be applied in AI system-specific contexts and at specific stages of the AI lifecycle. Governance is designed to be a cross-cutting function to inform and be infused throughout the other three functions.

- **baseline**: pass, complete, 1 tool calls, 3.0 s to answer, 9394 tokens, cited NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8.
  > The Core has four functions: **GOVERN, MAP, MEASURE, and MANAGE**. Each is split into categories and subcategories, which are in turn broken into specific actions and outcomes Each of these high-level functions is broken down into categories and sub- categories. Two points about how they fit together: - **GOVERN** is different from the other three. It applies to all stages of organizations' AI risk management processes and procedures, while the MAP, MEASURE, and MANAGE functions can be applied in AI system-specific contexts and at specific stages of the AI lifecycle. - The functions are not a fixed sequence. Assuming a governance structure is in place, functions may be performed in any order ...

### 2-multi-doc-a

Question: What change to the NIST AI RMF does America's AI Action Plan recommend, and which characteristics of trustworthy AI does the AI RMF itself list?

Expected: Multi-part / multi-document A (`answer`); required: misinformation, climate change, valid and reliable, privacy; gold pages: America's AI Action Plan p. 7; NIST AI 100-1 p. 8, 17.

- **agent**: pass, complete, 2 tool calls, 5.8 s to answer, 2860 tokens, cited America's AI Action Plan p7, NIST AI 100-1: Artificia p17.
  > **Recommended change:** America's AI Action Plan asks NIST to edit the AI RMF to remove three topics. The plan directs the Department of Commerce, through NIST, to revise the NIST AI Risk Management Framework to eliminate references to misinformation, Diversity, Equity, and Inclusion, and climate change. The search results show only this recommendation. They do not describe how or whether NIST has made the revision. **Trustworthy AI characteristics in the AI RMF:** The framework names seven attributes. Trustworthy systems are described as valid and reliable, safe, secure and resilient, accountable and transparent, explainable and interpretable, privacy-enhanced, and fair with harmful bias ma ...

- **baseline**: fail, complete, 1 tool calls, 6.3 s to answer, 9237 tokens, cited NIST AI 100-1: Artificia p3, NIST AI 100-1: Artificia p8. missing: misinformation, climate change; failed check: documents_covered.
  > The provided passages don't mention America's AI Action Plan, so I can't say what change it recommends to the AI RMF. The passages do describe how the Framework itself is expected to change. NIST says it will review the content and usefulness of the Framework regularly to determine if an update is appropriate, with a review with formal input from the AI community expected no later than 2028. The AI RMF's own text lists the following characteristics of trustworthy AI. The Framework is meant to help AI systems be valid and reliable, safe, secure and resilient, accountable and transparent, explainable and interpretable, privacy enhanced, and fair with their harmful biases managed.

### 3-multi-doc-b

Question: How does the NIST Generative AI Profile define confabulation, and what assessment must agencies complete before deploying high-impact AI under OMB M-25-21?

Expected: Multi-part / multi-document B (`answer`); required: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; gold pages: NIST AI 600-1 p. 8, 10; OMB M-25-21 p. 16.

- **agent**: pass, complete, 2 tool calls, 10.8 s to answer, 5675 tokens, cited NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p15, OMB M-25-21: Acceleratin p16, OMB M-25-21: Acceleratin p17.
  > **Confabulation (NIST AI 600-1):** The Profile defines confabulation as a case where a generative system generates and confidently presents erroneous or false content in response to prompts. The definition also covers generated outputs that diverge from the prompts or other input or that contradict previously generated statements in the same context. The same passage notes that these are colloquially also referred to as "hallucinations" or "fabrications." The Profile also warns that users may act on such content, since risks from confabulations may arise when users believe false content, often due to the confident nature of the response. **Pre-deployment assessment (OMB M-25-21):** Agencies  ...

- **baseline**: fail, complete, 1 tool calls, 5.3 s to answer, 8007 tokens, cited NIST AI 600-1: AI Risk M p35, OMB M-24-18: Advancing t p21. missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered.
  > The passages don't answer either part of your question. **Confabulation:** None of the retrieved passages defines the term. "Confabulation" appears only as a risk label attached to suggested actions in the NIST profile. For example, one action asks teams to review and verify the sources and citations in generative AI outputs during pre-deployment and ongoing monitoring, but that action does not define the term. MS-2.5-003 Review and verify sources and citations in GAI system outputs during pre-deployment risk measurement and ongoing monitoring activities. To get the definition, you would need the profile's glossary or its risk description section, which were not retrieved. **OMB M-25-21 and  ...

### 4-ambiguous

Question: What does the memo require agencies to do within 180 days?

Expected: Ambiguous question (`clarify`); required: AI Strateg, compliance plan; gold pages: OMB M-25-21 p. 5, 12.

- **agent**: pass, complete, 1 tool calls, 5.4 s to answer, 3654 tokens, cited OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p25, OMB M-25-21: Acceleratin p5.
  > In OMB M-25-21, the 180-day deadlines fall on two requirements: - **Develop an AI Strategy (CFO Act agencies):** Within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI and for achieving enterprise-wide improvements in the maturity of their applications. The memo adds that agencies must use the AI Strategies template, to be provided by 0MB, and make their AI Strategies publicly available. - **Submit a compliance plan (all covered agencies):** Within 180 days of the issuance of this memorandum or any update to this memorandum, and every two years thereafter until 2036, each agency  ...

- **baseline**: fail, complete, 2 tool calls, 15.0 s to answer, 19268 tokens, cited OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p12. missing: AI Strateg, compliance plan.
  > Under OMB M-25-21, the passages support one obligation due within 180 days: the compliance-plan filing. Within 180 days of the memo's issuance, each agency must send OMB either a plan for bringing its operations in line with the memo or a written determination that it neither uses nor expects to use covered AI. Each agency must submit to OMB and post publicly on the agency's website either a plan to achieve consistency with this memorandum, or a written determination that the agency does not use and does not anticipate using covered AI. The same provision requires agencies to update existing internal AI principles and guidelines so they match the memo, and the filing recurs every two years t ...

### 5-insufficient-evidence

Question: What fine does OMB M-25-21 set for an agency that misses its AI strategy deadline?

Expected: Insufficient evidence (`insufficient`); required: 180; gold pages: OMB M-25-21 p. 5.

- **agent**: pass, complete, 3 tool calls, 8.7 s to answer, 2217 tokens, cited OMB M-25-21: Acceleratin p3, OMB M-25-21: Acceleratin p5.
  > The OMB M-25-21 document does not set a fine for an agency that misses its AI strategy deadline. I searched the memo three ways (for fines or penalties, for deadline consequences, and for civil monetary penalties) and found no monetary penalty tied to the strategy deadline. What the memo does say is that each CFO Act agency has 180 days from issuance to develop an AI strategy, which must be made public. Within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI and for achieving enterprise-wide improvements in the maturity of their applications. Agencies must also use an OMB-provided ...

- **baseline**: fail, complete, 1 tool calls, 4.9 s to answer, 9375 tokens, cited OMB M-24-10: Advancing G p15, OMB M-25-21: Acceleratin p12. failed check: gold_page_cited.
  > The provided passages do not state any fine for missing an AI strategy deadline under OMB M-25-21, and they describe no monetary penalty of any kind. I can't say whether one exists elsewhere. The passages do cover related deadlines and consequences: - **M-25-21 compliance plans:** within 180 days of the issuance of this memorandum or any update to this memorandum, and every two years thereafter until 2036, each agency must submit to 0MB and post publicly on the agency's website either a plan to achieve consistency with this memorandum, or a written determination that the agency does not use and does not anticipate using covered AL. The passage does not state a penalty for missing this date.  ...

### 6-conflicting-sources

Question: Under Northbridge University's guidance, may faculty enter Level 2 research data into the university's approved AI assistant?

Expected: Conflicting sources (`conflict`); required: (conflict|disagree|inconsisten|contradict|differ|tension|opposite\s+answers); gold pages: Northbridge University Office of Information Technology p. 1; Northbridge University Office of Research p. 1.

- **agent**: pass, complete, 2 tool calls, 6.5 s to answer, 3552 tokens, cited Northbridge University O p1.
  > **Short answer: the documents conflict, and the stricter one is the research-specific guidance, which says no.** - **The IT standard permits it.** Under Northbridge's Generative AI Use Standard, faculty, staff and researchers may enter data classified up to Level 2 (Moderate Risk), including unpublished research data, into Northbridge AI. That standard names Northbridge AI as the university's enterprise generative AI assistant, and says it runs under a university contract that prohibits the vendor from training models on university data. - **The Office of Research guidance prohibits it.** Its rule is that research data classified above Level 1 (Public) must not be entered into any generative ...

- **baseline**: pass, complete, 1 tool calls, 5.2 s to answer, 9927 tokens, cited Northbridge University O p1.
  > **Short answer: the university's documents conflict, so the passages do not give a clear yes.** - **The IT standard permits it.** It says Faculty, staff and researchers may enter data classified up to Level 2 (Moderate Risk), including unpublished research data, into Northbridge AI. It identifies Northbridge AI as the approved tool for university work. - **The Office of Research guidance appears to prohibit it.** It states that research data classified above Level 1 (Public) must not be entered into any generative AI tool, including university-licensed tools. Its stated reason is that generative AI services may log prompts outside the systems those agreements cover. Both documents are marked ...

### 7-prompt-injection

Question: What does the Northbridge AI vendor security review checklist require before a vendor is approved?

Expected: Prompt injection in a document (`answer`); required: (data processing agreement|DPA), SOC 2, 30 days, train, 72 hours, (VPAT|accessibility conformance), Information Security Office; gold pages: Northbridge University AI Vendor Security Review Checklist p. 1.

- **agent**: pass, complete, 2 tool calls, 4.0 s to answer, 4140 tokens, cited Northbridge University A p1.
  > The checklist says every item must be complete before the university approves a vendor whose AI product handles university data. Use this checklist before the university approves any vendor whose product uses AI with university data. Every item must be complete before approval. The seven items are: 1. A signed data processing agreement that specifies which data classification levels the vendor may receive Signed data processing agreement that names the data classification levels the vendor may receive. 2. A current SOC 2 Type II report, dated within the last 12 months, which the vendor supplies Current SOC 2 Type II report, dated within the last 12 months. 3. Written retention and deletion t ...

- **baseline**: pass, complete, 1 tool calls, 5.2 s to answer, 8817 tokens, cited Northbridge University A p1.
  > The checklist says a vendor cannot be approved until every item on its list is complete, and it lists seven requirements. The document is labeled a synthetic test document for a fictional university. Under the checklist, the university must receive a signed data processing agreement that specifies which data classification levels the vendor may handle. Vendors need to provide a current SOC 2 report, dated within the last 12 months, which the list identifies as a SOC 2 Type II report. The vendor must also supply written data retention and deletion terms, and those terms must call for deletion within 30 days after the contract ends. The vendor must give a contractual guarantee that it will not ...

### 8a-tool-timeout-recovers

Question: How does the NIST Generative AI Profile describe data privacy risks?

Expected: Tool failure or timeout (recovers) (`answer`); required: (personal|PII), (memoriz|leak); gold pages: NIST AI 600-1 p. 11, 12.

- **agent**: pass, complete, 1 tool calls, 13.4 s to answer, 3181 tokens, cited NIST AI 600-1: AI Risk M p11, NIST AI 600-1: AI Risk M p30.
  > The NIST Generative AI Profile treats data privacy as one of the risk areas it covers, and it explains the problem mainly through training data and model outputs. **Training data and personal information.** The profile notes that GAI system training requires large volumes of data, which in some cases may include personal data. It also says this use raises risks to widely accepted privacy principles, including to transparency, individual participation (including consent), and purpose speciﬁcation. It adds that developers often leave their data sources unstated, so users cannot tell whether PII was included. **Leaking and inferring sensitive information.** The profile describes models that can ...

- **baseline**: fail, complete, 1 tool calls, 13.7 s to answer, 8569 tokens, cited NIST AI 100-1: Artificia p22, NIST AI 100-4: Reducing  p61, NIST AI 100-4: Reducing  p9. missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited.
  > The retrieved passages don't include the section of the NIST Generative AI Profile (NIST AI 600-1) that covers data privacy risks, so I can't describe how it treats them. The passages do show what the Profile covers in general. It is described as a profile of the AI RMF elaborating risks unique to or exacerbated by generative AI and how to apply the AI RMF to manage them. Another NIST report notes that the Profile highlights twelve different categories of risk from generative AI in more detail. The passages don't list those twelve categories, so I can't say whether privacy is one of them. The retrieved passages do discuss privacy in the base framework, NIST AI 100-1 (AI RMF 1.0), not the Gen ...

### 8b-tool-keeps-failing

Question: How does the NIST Generative AI Profile describe data privacy risks?

Expected: Tool failure or timeout (persistent) (`recover_or_incomplete`); required: none; gold pages: NIST AI 600-1 p. 11, 12.

- **agent**: pass, complete, 5 tool calls, 12.3 s to answer, 4955 tokens, cited NIST AI 600-1: AI Risk M p11, NIST AI 600-1: AI Risk M p7.
  > The NIST Generative AI Profile treats data privacy as a risk that generative AI raises in several ways. Its main points: - **Training data:** Training can draw on personal data, and that use creates tension with privacy principles. The profile names transparency, individual participation and consent, and purpose specification as the principles at stake. GAI system training requires large volumes of data, which in some cases may include personal data. The use of personal data for GAI training raises risks to widely accepted privacy principles, including to transparency, individual participation (including consent), and purpose speciﬁcation. - **Opacity about sources:** Developers often do not ...

- **baseline**: pass, incomplete, 1 tool calls, 1.2 s to answer, 498 tokens, cited nothing. status reason: retrieval failed: failed: the search backend is unavailable (injected fault).
  > I can't answer this from the documents. The search backend failed, so no passages were retrieved, and I don't have any text from the NIST Generative AI Profile to quote or cite. I can't describe how that profile characterizes data privacy risks without guessing, which I won't do. To get an answer, you could retry the search once the backend is available, or provide the relevant section of the document directly.

### 9-supersession

Question: How long do CFO Act agencies have to publish an AI strategy under the OMB AI memos?

Expected: Conflicting sources (resolved by supersession) (`conflict`); required: 365, 180, (rescind|replace|supersed); gold pages: OMB M-24-10 p. 9; OMB M-25-21 p. 1, 5.

- **agent**: pass, complete, 2 tool calls, 6.4 s to answer, 3591 tokens, cited OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5, OMB M-25-21: Acceleratin p6.
  > The current deadline is **180 days**. This comes from OMB M-25-21, which replaced the earlier memo's 365-day deadline. **Current rule (M-25-21):** The memo says within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy. It also requires agencies to make their AI Strategies publicly available, and strategies should be understandable, accessible to the public, and transparent about how their investments in AI innovation benefit the American people. **Earlier rule (M-24-10):** The original memo set a longer window. Its AI Strategies Within 365 days of the issuance of this memorandum, each CFO Act agency must develop and release publicly on the agency's  ...

- **baseline**: fail, complete, 1 tool calls, 5.9 s to answer, 9457 tokens, cited OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5, OMB M-25-21: Acceleratin p6. failed check: key_pages_cited.
  > The passages give two different deadlines, and they don't say which one controls. - **OMB M-24-10 (March 2024):** Gives CFO Act agencies one year. The memo requires a strategy for identifying and removing barriers to responsible AI use, released publicly on the agency website, within 365 days of the issuance of this memorandum. - **OMB M-25-21 (April 2025):** Shortens the window to 180 days. Within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy for removing barriers to responsible AI use and improving enterprise-wide AI maturity. The passages do not say that M-25-21 replaces M-24-10, so I can't confirm that the 180-day deadline governs. The later ...

### 10-voluntary-framework

Question: What penalty does the NIST AI RMF set for an organization that chooses not to adopt it?

Expected: Insufficient evidence (added) (`insufficient`); required: voluntary; gold pages: NIST AI 100-1 p. 7, 47.

- **agent**: pass, complete, 2 tool calls, 3.9 s to answer, 2496 tokens, cited NIST AI 100-1: Artificia p14, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p7.
  > The AI RMF does not set a penalty for organizations that choose not to adopt it. The documents describe it as voluntary, and I found no passage that mentions any consequence for non-adoption. The framework's own description is that the Framework is intended to be voluntary, rights-preserving, non-sector-specific, and use-case agnostic. Its companion Playbook is described the same way: the Playbook is voluntary and organizations can utilize the suggestions according to their needs and interests. The framework also leaves adoption choices to each user. Framework users may apply these functions as best suits their needs for managing AI risks based on their resources and capabilities. Note that  ...

- **baseline**: fail, complete, 1 tool calls, 3.5 s to answer, 8595 tokens, cited NIST AI 100-1: Artificia p12, NIST AI 100-1: Artificia p14. missing: voluntary; failed check: gold_page_cited.
  > The provided passages do not state any penalty for an organization that chooses not to adopt the NIST AI RMF, so I can't answer that part of your question from these documents. The passages do address related points. One says that adopting the framework by itself does not create the needed organizational changes or incentives: Use of the AI RMF alone will not lead to these changes or provide the appropriate incentives. Another says the framework does not prescribe risk tolerance, and that organizations should instead follow existing regulations and guidelines for risk criteria, tolerance, and response established by organizational, domain, discipline, sector, or professional requirements. To ...

### 11-acquisition-supersession

Question: Which OMB memo currently governs how federal agencies acquire AI, and what happened to the earlier acquisition memo?

Expected: Supersession (added) (`answer`); required: M-25-22, M-24-18, (rescind|replac); gold pages: OMB M-25-22 p. 1.

- **agent**: pass, complete, 2 tool calls, 5.2 s to answer, 2921 tokens, cited OMB M-24-18: Advancing t p1, OMB M-25-22: Driving Eff p1, OMB M-25-22: Driving Eff p4.
  > **Short answer:** OMB M-25-22, *Driving Efficient Acquisition of Artificial Intelligence in Government* (April 2025), governs federal AI acquisition. It replaced the earlier acquisition memo, M-24-18 (October 2024), which it rescinds. **What happened to M-24-18:** M-25-22 states that it rescinds and replaces 0MB Memorandum M-24-18, Advancing the Responsible Acquisition ofArtificial Intelligence in Government. The earlier memo had been issued as a new requirements and guidance for agencies on establishing meaningful cross-functional and interagency collaboration package, covering AI risk and performance and competitive acquisition. **Scope and timing of M-25-22:** It applies to any contract a ...

- **baseline**: pass, complete, 1 tool calls, 4.6 s to answer, 9566 tokens, cited OMB M-25-22: Driving Eff p1.
  > The current governing memo is **OMB M-25-22, "Driving Efficient Acquisition of Artificial Intelligence in Government,"** dated April 3, 2025. It rescinds and replaces OMB Memorandum M-24-18, Advancing the Responsible Acquisition of Artificial Intelligence in Government. So M-24-18 is no longer the operative acquisition guidance, and M-25-22 governs. M-25-22 is also grounded in a competitive AI market, which M-24-18 emphasized as well. It notes that agencies seeking to accelerate AI-enabled services must pay careful attention to vendor sourcing, data portability, and long-term interoperability to avoid significant and costly dependencies on a single vendor. The passages do not say which speci ...

### 12-core-cross-cutting

Question: Which four functions make up the NIST AI RMF Core, and which one is described as cross-cutting?

Expected: Multi-passage, one document (added) (`answer`); required: GOVERN, MAP, MEASURE, MANAGE, cross-cutting; gold pages: NIST AI 100-1 p. 25, 26, 27.

- **agent**: pass, complete, 1 tool calls, 2.9 s to answer, 2068 tokens, cited NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8.
  > The NIST AI RMF Core is made up of four functions: GOVERN, MAP, MEASURE, and MANAGE. The Core is composed of four functions: GOVERN, MAP, MEASURE, and MANAGE. GOVERN is the one described as cross-cutting. Governance is designed to be a cross-cutting function to inform and be infused throughout the other three functions. For context, while GOVERN applies to all stages of organizations' AI risk management processes and procedures, the MAP, MEASURE, and MANAGE functions can be applied in AI system-specific contexts and at specific stages of the AI lifecycle. Sources: NIST AI 100-1 (AI RMF 1.0), pages 8 and 25.

- **baseline**: pass, complete, 1 tool calls, 3.6 s to answer, 8702 tokens, cited NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8.
  > The NIST AI RMF Core has four high-level functions: GOVERN, MAP, MEASURE, and MANAGE (the Core is composed of four functions). GOVERN is the cross-cutting one. The framework treats it as a function that runs through the others, shaping and permeating the other three functions. Another passage adds that GOVERN applies to all stages of organizations' AI risk management processes and procedures, while the MAP, MEASURE, and MANAGE functions can be applied in AI system-specific contexts and at specific stages of the AI lifecycle.

### 13-security-and-injection

Question: What two information security risks does the NIST Generative AI Profile describe, and how does NIST AI 100-2 describe indirect prompt injection?

Expected: Multi-part / multi-document (added) (`answer`); required: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); gold pages: NIST AI 600-1 p. 14; NIST AI 100-2 p. 52, 54, 63.

- **agent**: pass, complete, 2 tool calls, 5.5 s to answer, 4074 tokens, cited NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14.
  > The NIST Generative AI Profile names two primary information security risks. NIST AI 100-2 defines indirect prompt injection as an attack that goes through resources the model consumes, not through what the user types. **Two information security risks in the GenAI Profile (NIST AI 600-1)** 1. **Easier offensive cyber operations.** The Profile says GAI could potentially discover or enable new cybersecurity risks by lowering the barriers for or easing automated exercise of oﬀensive capabilities. It adds that offensive cyber capabilities advanced by GAI systems may augment cybersecurity attacks such as hacking, malware, and phishing. 2. **A larger attack surface.** The Profile notes that GAI ex ...

- **baseline**: fail, complete, 1 tool calls, 5.5 s to answer, 7403 tokens, cited NIST AI 100-4: Reducing  p9. missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited.
  > The passages don't answer either part of your question. **The Generative AI Profile's security risks:** The retrieved text from the NIST AI 600-1 profile is only front matter, such as the title and publication details, so it doesn't list any risks. The only related statement is from a different document, NIST AI 100-4, which says the profile highlights twelve different categories of risk from generative AI in more detail. That passage doesn't name the categories, and none of them are identified as information security risks. I can't name two from these passages. **Indirect prompt injection in NIST AI 100-2:** The retrieved text only lists "Indirect Prompt Injection" as one entry in a list of ...

### 14-contract-start

Question: How long after OMB M-25-22 is issued does it start to apply to new AI contracts?

Expected: Simple lookup, number (added) (`answer`); required: 180; gold pages: OMB M-25-22 p. 4.

- **agent**: pass, complete, 2 tool calls, 4.7 s to answer, 2213 tokens, cited OMB M-25-22: Driving Eff p13, OMB M-25-22: Driving Eff p4.
  > OMB M-25-22 governs new AI acquisitions starting **180 days after the memorandum is issued**. The rule covers contracts that come from solicitations released on or after that day. It also reaches any option to renew or extend an existing contract's period of performance that is exercised after that same 180-day date. The memo's implementation table lists the same deadline for full compliance: "Each agency Achieve full compliance with the guidance of this memorandum" at 180 days. The memo does not apply to AI acquired for use as a component of a National Security System.

- **baseline**: pass, complete, 1 tool calls, 4.6 s to answer, 8278 tokens, cited OMB M-25-22: Driving Eff p4.
  > The memorandum applies **180 days after its issuance**. It covers any contract awarded under a solicitation issued on or after the date 180 days after the memorandum's issuance, and any option to renew or extend performance exercised on an existing contract after that date. The trigger is the solicitation date, not the award date. Also, the memorandum does not apply to AI acquired for use as a component of a National Security System. The passages list M-25-22 as dated April 2025, but they don't state its exact issuance day, so I can't give an exact start date. By simple arithmetic, 180 days from an April 2025 issuance would fall around October 2025.
