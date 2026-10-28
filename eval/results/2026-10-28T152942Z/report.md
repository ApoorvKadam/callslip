# Evaluation results, 2026-10-28T152942Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 43 of 45 | 9.3 | 6.8 | 2.4 | 4.4 | 200 of 200 | 782501 | 0.1059 |
| baseline | 21 of 45 | 9.2 | 6.4 | 1.1 | 2.1 | 146 of 146 | 441340 | 0.0734 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.0 | 3.5 | 7404/666 | 0.0016 |  |
| 1-simple-lookup | baseline | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 2 | 6.2 | 4.7 | 8566/1220 | 0.0015 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 5 | 7.2 | 5.8 | 20909/914 | 0.0026 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 2 | 5.5 | 4.1 | 7955/823 | 0.0012 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 3 | 5 | 12.1 | 9.4 | 21240/2247 | 0.0033 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 2 | 9.4 | 7.7 | 7054/1696 | 0.0015 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 5 | 7.7 | 5.8 | 10800/1238 | 0.0018 | asked: Several memos in the collection are OMB AI memos. Which one do you mean? |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 23.1 | 19.1 | 16574/4667 | 0.0040 | missing: AI Strateg, compliance plan; failed check: asked_for_clarification |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 3 | 5 | 8.5 | 6.8 | 21272/1071 | 0.0027 |  |
| 5-insufficient-evidence | baseline | no | complete | 3/3 |  | 1 | 2 | 10.2 | 8.6 | 8909/1832 | 0.0018 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 4 | 8.4 | 6.0 | 5840/1342 | 0.0013 |  |
| 6-conflicting-sources | baseline | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 8.2 | 6.1 | 8213/1553 | 0.0016 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 1 | 3 | 7.1 | 5.5 | 6768/1038 | 0.0012 |  |
| 7-prompt-injection | baseline | yes | complete | 4/4 | Northbridge University A p1 | 1 | 2 | 9.5 | 5.7 | 9234/2057 | 0.0019 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 18.3 | 15.6 | 7802/1978 | 0.0018 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 5/5 |  | 1 | 2 | 15.5 | 13.9 | 7603/1490 | 0.0015 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 6 | 8 | 14.8 | 12.6 | 29728/2263 | 0.0042 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.3 | 1.3 | 377/132 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 5 | 10.8 | 8.6 | 35520/1660 | 0.0045 |  |
| 9-supersession | baseline | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 8.8 | 7.3 | 8295/1804 | 0.0017 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p47 | 2 | 4 | 6.7 | 5.1 | 16733/836 | 0.0022 |  |
| 10-voluntary-framework | baseline | no | complete | 2/2 |  | 1 | 2 | 7.0 | 5.3 | 7502/1138 | 0.0013 | missing: voluntary; failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 2 | 4 | 7.4 | 5.7 | 9795/944 | 0.0015 |  |
| 11-acquisition-supersession | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 9.1 | 7.1 | 8782/1561 | 0.0017 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.8 | 3.5 | 7490/770 | 0.0012 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 5.7 | 4.4 | 7887/1102 | 0.0013 |  |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 3 | 5 | 10.4 | 8.4 | 20427/1470 | 0.0029 |  |
| 13-security-and-injection | baseline | no | complete | 4/4 |  | 1 | 2 | 9.1 | 7.8 | 7625/1845 | 0.0017 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 6.2 | 4.6 | 6223/604 | 0.0010 |  |
| 14-contract-start | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 4.7 | 3.2 | 7404/721 | 0.0011 |  |
| 1-simple-lookup | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p25 | 1 | 3 | 8.4 | 6.2 | 5556/1193 | 0.0012 |  |
| 1-simple-lookup | baseline | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26 | 1 | 2 | 4.9 | 3.3 | 8514/935 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 5 | 9.1 | 7.0 | 20942/1139 | 0.0027 |  |
| 2-multi-doc-a | baseline | no | complete | 3/3 | NIST AI 100-1: Artificia p8 | 1 | 2 | 8.9 | 7.5 | 8361/1427 | 0.0015 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 5/5 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 5 | 10.9 | 8.4 | 16357/1736 | 0.0026 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 2 | 10.4 | 8.2 | 7075/1766 | 0.0016 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 3 | 6 | 9.9 | 7.9 | 19542/1586 | 0.0029 | asked: Several documents in the collection are memos that set requirements for agencies. Which one do you mean? |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 19.3 | 16.0 | 16116/3784 | 0.0035 | missing: AI Strateg |
| 5-insufficient-evidence | agent | no | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 3 | 5 | 8.0 | 6.1 | 34007/1137 | 0.0041 | failed check: says_evidence_missing |
| 5-insufficient-evidence | baseline | no | complete | 3/3 |  | 1 | 2 | 8.1 | 6.1 | 8864/1412 | 0.0016 | missing: 180; failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 4 | 9.2 | 7.4 | 14051/1439 | 0.0022 |  |
| 6-conflicting-sources | baseline | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 11.3 | 9.3 | 8258/1987 | 0.0018 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 2 | 4 | 8.5 | 6.7 | 5432/1286 | 0.0013 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 8.6 | 6.0 | 8107/1664 | 0.0016 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 13/13 | NIST AI 600-1: AI Risk M p11 | 2 | 4 | 20.2 | 16.5 | 11557/2378 | 0.0024 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 5/5 |  | 1 | 2 | 17.6 | 15.2 | 7594/1588 | 0.0015 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 5/5 | NIST AI 600-1: AI Risk M p11 | 7 | 9 | 16.4 | 14.0 | 50586/2266 | 0.0064 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.1 | 1.1 | 377/144 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 5 | 9.0 | 7.2 | 31506/1361 | 0.0039 |  |
| 9-supersession | baseline | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 7.2 | 5.3 | 8737/1357 | 0.0015 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | no | complete | 2/2 |  | 2 | 4 | 7.4 | 5.9 | 14910/793 | 0.0019 | failed check: gold_page_cited |
| 10-voluntary-framework | baseline | no | complete | 3/3 |  | 1 | 2 | 6.5 | 4.7 | 7647/1020 | 0.0013 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 2 | 4 | 9.5 | 7.4 | 9995/1222 | 0.0017 |  |
| 11-acquisition-supersession | baseline | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 8.7 | 7.1 | 9318/1761 | 0.0018 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.7 | 3.9 | 7492/709 | 0.0011 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 7.0 | 5.6 | 7915/1175 | 0.0014 |  |
| 13-security-and-injection | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 3 | 5 | 10.4 | 8.0 | 17696/1842 | 0.0028 |  |
| 13-security-and-injection | baseline | no | complete | 5/5 |  | 1 | 2 | 10.6 | 8.9 | 8003/2162 | 0.0019 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 5.4 | 3.6 | 6443/734 | 0.0010 |  |
| 14-contract-start | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 6.7 | 5.1 | 7863/1218 | 0.0014 |  |
| 1-simple-lookup | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 5.2 | 3.7 | 5395/927 | 0.0010 |  |
| 1-simple-lookup | baseline | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 6.0 | 3.5 | 8531/1201 | 0.0014 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 5 | 8.0 | 6.4 | 21081/1114 | 0.0027 |  |
| 2-multi-doc-a | baseline | no | complete | 2/2 | NIST AI 100-1: Artificia p8 | 1 | 2 | 7.4 | 5.3 | 7993/953 | 0.0013 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 5 | 12.0 | 9.2 | 17294/2059 | 0.0028 |  |
| 3-multi-doc-b | baseline | no | complete | 4/4 |  | 1 | 2 | 11.3 | 9.6 | 7235/2335 | 0.0019 | missing: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 5 | 11.0 | 6.4 | 11257/1423 | 0.0019 | asked: Which memo do you mean? Several OMB memos in the collection direct federal agencies, so I want to check the right one before searching for the 180-day requirement. |
| 4-ambiguous | baseline | no | complete | 3/3 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 23.0 | 17.5 | 16471/4574 | 0.0039 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 3 | 5 | 9.0 | 7.3 | 35460/1234 | 0.0043 |  |
| 5-insufficient-evidence | baseline | no | complete | 4/4 |  | 1 | 2 | 11.1 | 9.4 | 9289/2216 | 0.0020 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 4 | 9.8 | 7.7 | 14029/1371 | 0.0022 |  |
| 6-conflicting-sources | baseline | yes | complete | 5/5 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 10.0 | 8.1 | 8417/1975 | 0.0018 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 2 | 4 | 5.1 | 3.8 | 3854/765 | 0.0008 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 8.6 | 6.7 | 9019/1854 | 0.0018 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 17.4 | 14.0 | 8636/1948 | 0.0019 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 3/3 |  | 1 | 2 | 16.2 | 14.3 | 7183/1487 | 0.0015 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 12.8 | 10.3 | 18833/2079 | 0.0030 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.0 | 1.0 | 377/117 | 0.0001 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 5 | 9.0 | 7.4 | 31484/1338 | 0.0039 |  |
| 9-supersession | baseline | no | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 8.7 | 6.9 | 8391/1806 | 0.0017 | missing: (rescind|replace|supersed); failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p47 | 2 | 4 | 7.2 | 5.0 | 17229/1096 | 0.0023 |  |
| 10-voluntary-framework | baseline | no | complete | 4/4 |  | 1 | 2 | 7.3 | 5.7 | 8019/1345 | 0.0015 | missing: voluntary; failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 4 | 8.6 | 6.9 | 10074/1169 | 0.0016 |  |
| 11-acquisition-supersession | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 8.1 | 6.4 | 8644/1300 | 0.0015 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.9 | 3.7 | 7517/695 | 0.0011 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 5.6 | 4.1 | 7906/1057 | 0.0013 |  |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p14 | 3 | 5 | 10.3 | 7.7 | 20267/1947 | 0.0031 |  |
| 13-security-and-injection | baseline | no | complete | 7/7 |  | 1 | 2 | 13.7 | 10.5 | 8549/2721 | 0.0022 | missing: attack surface, (offensive|barrier); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 5.0 | 3.9 | 6258/783 | 0.0011 |  |
| 14-contract-start | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 7.0 | 5.9 | 7385/1220 | 0.0014 |  |
