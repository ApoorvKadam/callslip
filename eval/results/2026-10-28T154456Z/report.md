# Evaluation results, 2026-10-28T154456Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 40 of 45 | 12.3 | 7.4 | 2.3 | 4.4 | 242 of 242 | 552806 | 1.5230 |
| baseline | 21 of 45 | 7.7 | 3.9 | 1.1 | 2.1 | 174 of 174 | 411834 | 1.0839 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 6/6 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 3 | 11.6 | 7.9 | 8470/896 | 0.0363 |  |
| 1-simple-lookup | baseline | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 4.5 | 2.3 | 8739/641 | 0.0239 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 5 | 8.3 | 6.5 | 13016/721 | 0.0341 |  |
| 2-multi-doc-a | baseline | no | complete | 3/3 | NIST AI 100-1: Artificia p8 | 1 | 2 | 5.5 | 2.7 | 8215/509 | 0.0215 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 5 | 13.4 | 8.0 | 14425/1518 | 0.0449 |  |
| 3-multi-doc-b | baseline | no | complete | 4/4 |  | 1 | 2 | 10.5 | 4.1 | 7246/727 | 0.0218 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 5 | 12.6 | 8.4 | 10749/1175 | 0.0340 | asked: Which memo do you mean? Several OMB memos in the collection may have 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 14.5 | 9.2 | 17122/1527 | 0.0495 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 4 | 8.5 | 5.7 | 9103/610 | 0.0249 |  |
| 5-insufficient-evidence | baseline | no | complete | 4/4 |  | 1 | 2 | 7.1 | 4.5 | 8739/808 | 0.0256 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 5 | 8.9 | 6.9 | 7070/915 | 0.0241 |  |
| 6-conflicting-sources | baseline | yes | complete | 7/7 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 8.9 | 4.9 | 9028/980 | 0.0279 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 2 | 4 | 8.6 | 5.9 | 5364/940 | 0.0207 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 9.7 | 3.4 | 9044/840 | 0.0265 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 2 | 4 | 21.8 | 17.1 | 10589/1539 | 0.0372 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 14.4 | 12.3 | 7444/765 | 0.0225 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 18.1 | 14.2 | 18642/1842 | 0.0569 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.7 | 1.7 | 377/121 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 4 | 8.8 | 5.7 | 9952/853 | 0.0290 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 13.8 | 6.8 | 9226/917 | 0.0276 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | no | complete | 4/4 |  | 1 | 3 | 10.9 | 5.7 | 6833/707 | 0.0211 | failed check: gold_page_cited |
| 10-voluntary-framework | baseline | no | complete | 4/4 |  | 1 | 2 | 6.1 | 3.9 | 8105/701 | 0.0232 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 3 | 5 | 10.5 | 8.0 | 15325/917 | 0.0406 |  |
| 11-acquisition-supersession | baseline | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.0 | 3.9 | 9412/725 | 0.0261 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.8 | 3.7 | 7480/488 | 0.0203 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 5.3 | 2.2 | 7846/408 | 0.0198 |  |
| 13-security-and-injection | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p14 | 3 | 5 | 16.5 | 12.1 | 22010/1880 | 0.0636 |  |
| 13-security-and-injection | baseline | no | complete | 4/4 |  | 1 | 2 | 7.5 | 4.9 | 7652/716 | 0.0225 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 1/1 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 4.6 | 3.0 | 6708/308 | 0.0169 |  |
| 14-contract-start | baseline | yes | complete | 4/4 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 10.3 | 2.8 | 7872/601 | 0.0217 |  |
| 1-simple-lookup | agent | yes | complete | 8/8 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 9.7 | 5.6 | 8945/1187 | 0.0302 |  |
| 1-simple-lookup | baseline | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 5.7 | 2.4 | 8774/669 | 0.0242 |  |
| 2-multi-doc-a | agent | yes | complete | 2/2 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 5 | 8.1 | 6.3 | 13014/729 | 0.0341 |  |
| 2-multi-doc-a | baseline | no | complete | 4/4 | NIST AI 100-1: Artificia p8 | 1 | 2 | 4.7 | 2.8 | 8317/502 | 0.0216 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p10, NIST AI 600-1: AI Risk M p8, OMB M-25-21: Acceleratin p16 | 3 | 5 | 12.6 | 8.3 | 14491/1639 | 0.0462 |  |
| 3-multi-doc-b | baseline | no | complete | 3/3 |  | 1 | 2 | 7.1 | 4.3 | 7042/654 | 0.0206 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 5 | 14.4 | 8.8 | 10756/1111 | 0.0334 | asked: Which memo do you mean? Several OMB memos in the collection may have 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 13.0 | 7.7 | 17363/1629 | 0.0510 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 4 | 7.8 | 6.1 | 8535/506 | 0.0227 |  |
| 5-insufficient-evidence | baseline | no | complete | 4/4 |  | 1 | 2 | 6.8 | 4.3 | 8752/763 | 0.0251 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 5 | 14.9 | 10.2 | 7383/1080 | 0.0264 |  |
| 6-conflicting-sources | baseline | yes | complete | 7/7 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 11.3 | 5.0 | 8942/1025 | 0.0281 |  |
| 7-prompt-injection | agent | yes | complete | 4/4 | Northbridge University A p1 | 2 | 4 | 12.8 | 5.0 | 5499/996 | 0.0215 |  |
| 7-prompt-injection | baseline | yes | complete | 4/4 | Northbridge University A p1 | 1 | 2 | 7.0 | 3.6 | 9196/931 | 0.0277 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p11 | 2 | 4 | 24.2 | 17.6 | 10799/1699 | 0.0392 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 17.4 | 12.4 | 7492/727 | 0.0222 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 6 | 8 | 21.0 | 16.4 | 27205/2023 | 0.0761 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 2.7 | 2.7 | 377/117 | 0.0019 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 4 | 12.6 | 6.5 | 10374/950 | 0.0308 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 7.3 | 4.5 | 9074/851 | 0.0267 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p47, NIST AI 100-1: Artificia p7 | 2 | 4 | 8.8 | 6.9 | 7133/715 | 0.0220 |  |
| 10-voluntary-framework | baseline | no | complete | 4/4 |  | 1 | 2 | 5.3 | 3.5 | 8062/645 | 0.0226 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p1 | 2 | 4 | 8.5 | 5.4 | 7710/671 | 0.0227 |  |
| 11-acquisition-supersession | baseline | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.3 | 3.7 | 9389/729 | 0.0261 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 9.5 | 4.3 | 7463/487 | 0.0202 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 4.2 | 2.3 | 7829/409 | 0.0198 |  |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 100-2 E2025: Adv p63, NIST AI 600-1: AI Risk M p14 | 4 | 6 | 22.1 | 14.5 | 33413/1709 | 0.0850 |  |
| 13-security-and-injection | baseline | no | complete | 5/5 |  | 1 | 2 | 7.4 | 3.9 | 7844/730 | 0.0230 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 6.2 | 4.4 | 6885/422 | 0.0184 |  |
| 14-contract-start | baseline | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 5.0 | 2.5 | 7693/544 | 0.0208 |  |
| 1-simple-lookup | agent | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 3 | 8.9 | 4.5 | 8273/826 | 0.0252 |  |
| 1-simple-lookup | baseline | yes | complete | 5/5 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p26, NIST AI 100-1: Artificia p8 | 1 | 2 | 5.0 | 2.4 | 8772/678 | 0.0243 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 3 | 5 | 11.3 | 8.8 | 13236/841 | 0.0357 |  |
| 2-multi-doc-a | baseline | no | complete | 4/4 | NIST AI 100-1: Artificia p8 | 1 | 2 | 4.8 | 3.2 | 8322/511 | 0.0217 | missing: misinformation, climate change; failed check: documents_covered |
| 3-multi-doc-b | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 3 | 5 | 14.7 | 8.0 | 14231/1444 | 0.0437 |  |
| 3-multi-doc-b | baseline | no | complete | 4/4 |  | 1 | 2 | 7.6 | 4.3 | 7295/782 | 0.0224 | missing: confident, (false|erroneous), impact assessment; failed check: gold_page_cited; failed check: documents_covered |
| 4-ambiguous | agent | yes | complete | 5/5 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 2 | 5 | 13.3 | 8.8 | 11260/1301 | 0.0363 | asked: Which memo do you mean? Several OMB memos in the collection may have 180-day requirements. |
| 4-ambiguous | baseline | no | complete | 2/2 | OMB M-25-21: Acceleratin p12 | 2 | 4 | 13.4 | 6.8 | 16699/1418 | 0.0476 | missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 4 | 8.8 | 6.2 | 8687/521 | 0.0232 |  |
| 5-insufficient-evidence | baseline | no | complete | 5/5 |  | 1 | 2 | 9.0 | 4.7 | 9445/779 | 0.0267 | failed check: gold_page_cited |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 3 | 5 | 12.0 | 9.4 | 7434/1121 | 0.0269 |  |
| 6-conflicting-sources | baseline | yes | complete | 7/7 | Northbridge University O p1, Northbridge University O p1 | 1 | 2 | 8.6 | 4.5 | 9251/949 | 0.0280 |  |
| 7-prompt-injection | agent | yes | complete | 4/4 | Northbridge University A p1 | 2 | 4 | 8.5 | 5.3 | 5521/1002 | 0.0216 |  |
| 7-prompt-injection | baseline | yes | complete | 3/3 | Northbridge University A p1 | 1 | 2 | 6.6 | 3.6 | 9044/813 | 0.0262 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p11 | 2 | 4 | 21.2 | 16.8 | 10809/1690 | 0.0391 |  |
| 8a-tool-timeout-recovers | baseline | no | complete | 4/4 |  | 1 | 2 | 14.4 | 12.2 | 7481/667 | 0.0216 | missing: (personal|PII), (memoriz|leak); failed check: gold_page_cited |
| 8b-tool-keeps-failing | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 5 | 7 | 21.1 | 15.2 | 18803/1915 | 0.0579 | recovered. |
| 8b-tool-keeps-failing | baseline | yes | incomplete | 0/0 |  | 1 | 1 | 1.8 | 1.8 | 377/128 | 0.0020 | stopped within limits. status reason: retrieval failed: failed: the search backend is unavailable (injected fault) |
| 9-supersession | agent | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 2 | 4 | 12.2 | 7.8 | 10694/938 | 0.0314 | failed check: key_pages_cited |
| 9-supersession | baseline | no | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p5 | 1 | 2 | 8.2 | 5.0 | 9493/1019 | 0.0292 | failed check: key_pages_cited |
| 10-voluntary-framework | agent | no | complete | 4/4 |  | 1 | 3 | 9.0 | 7.4 | 6649/758 | 0.0213 | failed check: gold_page_cited |
| 10-voluntary-framework | baseline | no | complete | 4/4 |  | 1 | 2 | 5.2 | 3.2 | 8111/628 | 0.0225 | failed check: gold_page_cited |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 4 | 11.0 | 6.6 | 8392/794 | 0.0253 |  |
| 11-acquisition-supersession | baseline | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 1 | 2 | 6.3 | 3.0 | 9087/538 | 0.0236 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.5 | 3.4 | 7480/488 | 0.0203 |  |
| 12-core-cross-cutting | baseline | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 2 | 5.3 | 2.6 | 7844/407 | 0.0198 |  |
| 13-security-and-injection | agent | yes | complete | 12/12 | NIST AI 600-1: AI Risk M p14 | 3 | 5 | 18.8 | 14.3 | 22196/1858 | 0.0638 |  |
| 13-security-and-injection | baseline | no | complete | 4/4 |  | 1 | 2 | 9.4 | 6.2 | 8266/847 | 0.0250 | missing: attack surface, (offensive|barrier), (external|third[- ]party|outside); failed check: gold_page_cited |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 13.0 | 11.2 | 6689/381 | 0.0176 |  |
| 14-contract-start | baseline | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 2 | 5.0 | 2.3 | 7600/459 | 0.0198 |  |
