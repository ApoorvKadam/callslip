# Evaluation results, 2026-10-28T220519Z

| System | Cases passed | Completed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|---|
| agent | 36 of 40 | 40 of 40 | 9.3 | 6.7 | 2.6 | 4.1 | 279 of 279 | 189746 | 0.0820 |

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

## Each case: expected and actual (first repeat)

### 8b-tool-keeps-failing

Question: How does the NIST Generative AI Profile describe data privacy risks?

Expected: Tool failure or timeout (persistent) (`recover_or_incomplete`); required: none; gold pages: NIST AI 600-1 p. 11, 12.

- **agent**: pass, complete, 3 tool calls, 6.7 s to answer, 4603 tokens, cited NIST AI 600-1: AI Risk M p11.
  > The NIST Generative AI Profile (NIST AI 600-1) treats data privacy as a distinct GAI risk in Section 2.4. The search tool failed, so I read pages 11–12 directly. **Core concern:** The profile warns that the use of personal data for GAI training raises risks to widely accepted privacy principles, including to transparency, individual participation (including consent), and purpose specification. **Opacity and exposure:** It notes that developers rarely reveal their training sources, so people often cannot tell whether their personal data was used. It adds that models may leak, generate, or correctly infer sensitive information about individuals. **Memorization:** The profile describes extracti ...

### 13-security-and-injection

Question: What two information security risks does the NIST Generative AI Profile describe, and how does NIST AI 100-2 describe indirect prompt injection?

Expected: Multi-part / multi-document (added) (`answer`); required: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); gold pages: NIST AI 600-1 p. 14; NIST AI 100-2 p. 52, 54, 63.

- **agent**: pass, complete, 2 tool calls, 7.5 s to answer, 4463 tokens, cited NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14.
  > **Information security risks in the NIST Generative AI Profile (NIST AI 600-1)** The Profile names two primary risks. First, generative AI could lower the cost of offensive cyber activity. GAI could potentially discover or enable new cybersecurity risks by lowering the barriers for or easing automated exercise of offensive capabilities. Second, the technology itself widens the target area: it expands the available attack surface, as GAI itself is vulnerable to attacks like prompt injection or data poisoning. **Indirect prompt injection in NIST AI 100-2** The glossary defines the term as a type of PROMPT INJECTION executed through RESOURCE CONTROL rather than through user-provided input as in ...
