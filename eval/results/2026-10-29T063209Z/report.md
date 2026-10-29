# Evaluation results, 2026-10-29T063209Z

| System | Cases passed | Completed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|---|
| agent | 15 of 15 | 15 of 15 | 7.8 | 5.7 | 1.9 | 3.6 | 77 of 77 | 60262 | 0.0347 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4-ambiguous | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.0 | 5.7 | 1434/1135 | 0.0017 | asked: Which memo do you mean? Several OMB AI memos in the collection set deadlines, so I want to check the right one. |
| 9-supersession | agent | yes | complete | 3/3 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 6.7 | 5.1 | 1673/1103 | 0.0032 |  |
| 13-security-and-injection | agent | yes | complete | 11/11 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 100-2 E2025: Adv p66, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.0 | 6.5 | 4217/2062 | 0.0026 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.9 | 6.2 | 2112/1349 | 0.0019 | asked: Which memo do you mean? Several OMB AI memos could contain 180-day requirements. |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 7.1 | 5.7 | 2050/1247 | 0.0033 |  |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 6.8 | 4.7 | 2727/1422 | 0.0020 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 7.6 | 5.8 | 1789/1302 | 0.0018 | asked: Several documents in the collection are OMB memos. Which one do you mean by "the memo" for the 180-day requirement? |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 3 | 8.4 | 6.0 | 3131/1448 | 0.0027 |  |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 8.1 | 5.4 | 3467/1783 | 0.0024 |  |
| 4-ambiguous | agent | yes | complete | 4/4 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 8.7 | 5.6 | 2219/1339 | 0.0019 | asked: Several OMB memos in the collection could be "the memo." Which one do you mean? |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 8.1 | 5.9 | 2101/1384 | 0.0027 |  |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 8.3 | 5.6 | 3375/1768 | 0.0022 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 6.9 | 5.2 | 2259/1383 | 0.0019 | asked: Which memo do you mean? Several documents in the collection are OMB memos that may set 180-day requirements. |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 8.0 | 5.8 | 2789/1481 | 0.0032 |  |
| 13-security-and-injection | agent | yes | complete | 6/6 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.8 | 5.6 | 3088/1625 | 0.0013 |  |

## Each case: expected and actual (first repeat)

### 4-ambiguous

Question: What does the memo require agencies to do within 180 days?

Expected: Ambiguous question (`clarify`); required: AI Strateg, compliance plan; gold pages: OMB M-25-21 p. 5, 12.

- **agent**: pass, complete, 1 tool calls, 5.7 s to answer, 2569 tokens, cited OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5.
  > In M-25-21, two obligations fall within 180 days, and both apply to agencies generally. - **Agency AI Strategy (CFO Act agencies):** Within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI and for achieving enterprise-wide improvements in the maturity of their applications. The strategy must follow the template OMB provides and be made public. - **Compliance plan (all covered agencies):** Within 180 days of the memo or any update to it, and every two years after that until 2036, each agency must send OMB a plan for consistency with the memo or a written determination that it does  ...

### 9-supersession

Question: How long do CFO Act agencies have to publish an AI strategy under the OMB AI memos?

Expected: Conflicting sources (resolved by supersession) (`conflict`); required: 365, 180, (rescind|replace|supersed); gold pages: OMB M-24-10 p. 9; OMB M-25-21 p. 1, 5.

- **agent**: pass, complete, 3 tool calls, 5.1 s to answer, 2776 tokens, cited OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5.
  > Under the current OMB memo, CFO Act agencies have **180 days** from the memo's issuance to develop an AI strategy. That deadline comes from OMB M-25-21, which replaced the earlier 365-day deadline in M-24-10. - **Current deadline (M-25-21):** Within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI. The memo also requires agencies to publish these strategies on their websites. - **Earlier deadline (M-24-10):** The prior memo gave 365 days of the issuance of this memorandum for CFO Act agencies to release a strategy. M-25-21 overrides this: this memorandum rescinds and replaces Offi ...

### 13-security-and-injection

Question: What two information security risks does the NIST Generative AI Profile describe, and how does NIST AI 100-2 describe indirect prompt injection?

Expected: Multi-part / multi-document (added) (`answer`); required: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); gold pages: NIST AI 600-1 p. 14; NIST AI 100-2 p. 52, 54, 63, 64, 65, 66, 67, 123.

- **agent**: pass, complete, 2 tool calls, 6.5 s to answer, 6279 tokens, cited NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 100-2 E2025: Adv p66, NIST AI 600-1: AI Risk M p14.
  > **NIST AI 600-1 (Generative AI Profile): two information security risks** The profile names two main risks. First, generative AI may lower the barrier to cyberattacks. GAI-based systems present two primary information security risks: GAI could potentially discover or enable new cybersecurity risks by lowering the barriers for or easing automated exercise of offensive capabilities. The profile adds that LLMs are already able to discover some vulnerabilities in systems (hardware, software, data) and write code to exploit them. Second, the models themselves widen the attack surface. The profile notes that the technology expands the available attack surface, as GAI itself is vulnerable to attack ...
