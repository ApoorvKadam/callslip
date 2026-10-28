# Evaluation results, 2026-10-28T220519Z

| System | Cases passed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|
| agent | 36 of 40 | 9.3 | 6.7 | 2.6 | 4.1 | 279 of 279 | 189746 | 0.0820 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.4 | 6.7 | 3059/1544 | 0.0026 | recovered. |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 10.0 | 7.5 | 2783/1680 | 0.0022 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.1 | 6.7 | 3275/1694 | 0.0020 | recovered. |
| 13-security-and-injection | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.1 | 6.6 | 3639/1914 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 11.9 | 6.4 | 2543/1454 | 0.0018 | recovered. |
| 13-security-and-injection | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.1 | 7.0 | 2978/1739 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 4 | 6 | 10.8 | 8.5 | 3042/1864 | 0.0022 | recovered. |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 8.3 | 6.1 | 3057/1707 | 0.0023 | missing: attack surface |
| 8b-tool-keeps-failing | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.8 | 6.3 | 2799/1515 | 0.0019 | recovered. |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.6 | 6.8 | 3735/1983 | 0.0024 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 10.0 | 6.8 | 2729/1557 | 0.0019 | recovered. |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 100-2 E2025: Adv p52, NIST AI 600-1: AI Risk M p14 | 3 | 4 | 10.0 | 7.9 | 2890/1906 | 0.0027 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.1 | 6.7 | 3080/1641 | 0.0020 | recovered. |
| 13-security-and-injection | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.9 | 6.9 | 3171/1816 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 1/1 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.0 | 6.9 | 1032/1010 | 0.0014 | recovered. |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 10.5 | 8.3 | 2945/1859 | 0.0023 | missing: (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input) |
| 8b-tool-keeps-failing | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.0 | 5.8 | 2705/1422 | 0.0018 | recovered. |
| 13-security-and-injection | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 10.4 | 7.2 | 4217/2154 | 0.0027 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.9 | 6.3 | 3098/1583 | 0.0013 | recovered. |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 100-2 E2025: Adv p63, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.9 | 7.1 | 4153/2058 | 0.0029 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.4 | 6.9 | 2811/1573 | 0.0017 | recovered. |
| 13-security-and-injection | agent | no | complete | 7/7 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 10.4 | 6.7 | 3170/1711 | 0.0023 | missing: attack surface |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.1 | 6.4 | 3101/1644 | 0.0020 | recovered. |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.7 | 5.3 | 2692/1401 | 0.0021 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.5 | 6.1 | 2671/1433 | 0.0018 | recovered. |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 8.5 | 6.0 | 2965/1518 | 0.0012 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.9 | 6.4 | 2857/1572 | 0.0019 | recovered. |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.0 | 6.5 | 3959/1956 | 0.0024 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.2 | 6.8 | 3052/1627 | 0.0013 | recovered. |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.8 | 5.6 | 3081/1581 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p11 | 4 | 5 | 8.9 | 6.7 | 2448/1449 | 0.0019 | recovered. |
| 13-security-and-injection | agent | yes | complete | 10/10 | NIST AI 100-2 E2025: Adv p63, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 10.1 | 7.0 | 4290/2103 | 0.0030 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 4/4 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 7.8 | 5.8 | 1795/1168 | 0.0009 | recovered. |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.5 | 6.9 | 3576/1816 | 0.0014 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 5/5 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.4 | 6.9 | 2470/1440 | 0.0018 | recovered. |
| 13-security-and-injection | agent | no | complete | 6/6 | NIST AI 600-1: AI Risk M p14 | 3 | 4 | 10.1 | 8.1 | 3011/2017 | 0.0028 | missing: (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input) |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 8.7 | 6.0 | 3327/1619 | 0.0013 | recovered. |
| 13-security-and-injection | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.6 | 6.6 | 3900/1928 | 0.0028 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 3 | 5 | 9.1 | 6.8 | 3087/1714 | 0.0014 | recovered. |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 600-1: AI Risk M p14 | 2 | 3 | 11.2 | 8.6 | 3412/1771 | 0.0022 |  |
