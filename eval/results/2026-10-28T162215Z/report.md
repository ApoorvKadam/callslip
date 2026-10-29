# Evaluation results, 2026-10-28T162215Z

| System | Cases passed | Completed | Mean latency (s) | Median time to answer (s) | Mean tool calls | Mean model calls | Citations verified | Total tokens | Total cost (USD) |
|---|---|---|---|---|---|---|---|---|---|
| agent | 42 of 45 | 45 of 45 | 8.9 | 6.3 | 2.0 | 3.4 | 215 of 215 | 158236 | 0.0984 |

| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited | Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 5.0 | 3.3 | 1665/835 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 7.5 | 5.6 | 1709/1289 | 0.0024 |  |
| 3-multi-doc-b | agent | no | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 9.1 | 6.5 | 2745/1896 | 0.0023 | missing: \bconfiden(?:t(?:ly)?|ce)\b |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 1 | 4 | 9.2 | 7.7 | 1511/1627 | 0.0019 | asked: Several documents in the collection are OMB memoranda. Which one do you mean by "the memo"? |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.4 | 4.8 | 1545/1157 | 0.0024 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 1 | 3 | 8.9 | 7.3 | 1687/1396 | 0.0014 |  |
| 7-prompt-injection | agent | yes | complete | 2/2 | Northbridge University A p1 | 1 | 3 | 5.8 | 4.5 | 1340/756 | 0.0009 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 17.3 | 14.4 | 3928/1914 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 6 | 6 | 15.3 | 12.8 | 2187/2848 | 0.0036 | recovered. |
| 9-supersession | agent | yes | complete | 4/4 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 2 | 4 | 9.3 | 5.8 | 1791/1322 | 0.0026 |  |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 4.8 | 3.7 | 1155/837 | 0.0021 |  |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 12.2 | 9.9 | 2032/2220 | 0.0030 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 5.8 | 4.1 | 1445/646 | 0.0015 |  |
| 13-security-and-injection | agent | no | complete | 11/11 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 100-2 E2025: Adv p66, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.9 | 7.0 | 3426/2188 | 0.0030 | missing: attack surface |
| 14-contract-start | agent | yes | complete | 2/2 | OMB M-25-22: Driving Eff p4 | 1 | 3 | 5.4 | 3.6 | 1366/741 | 0.0014 |  |
| 1-simple-lookup | agent | yes | complete | 4/4 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 6.0 | 4.4 | 1693/938 | 0.0013 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 7.1 | 5.5 | 1663/1314 | 0.0024 |  |
| 3-multi-doc-b | agent | yes | complete | 9/9 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 9.1 | 6.7 | 2804/2045 | 0.0024 |  |
| 4-ambiguous | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5 | 4 | 5 | 10.4 | 8.1 | 1955/1875 | 0.0029 | asked: Several documents in the collection set 180-day requirements for agencies. Which memo do you mean? |
| 5-insufficient-evidence | agent | yes | complete | 2/2 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.8 | 5.1 | 1220/1011 | 0.0022 |  |
| 6-conflicting-sources | agent | yes | complete | 4/4 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 9.0 | 6.9 | 2236/1631 | 0.0020 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 2 | 3 | 7.2 | 5.0 | 2613/1441 | 0.0013 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 10/10 | NIST AI 600-1: AI Risk M p11 | 2 | 3 | 18.2 | 15.4 | 3088/2069 | 0.0029 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 11/11 | NIST AI 600-1: AI Risk M p11 | 6 | 8 | 14.5 | 11.4 | 3772/2704 | 0.0043 | recovered. |
| 9-supersession | agent | yes | complete | 5/5 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 9.6 | 7.8 | 2075/1694 | 0.0032 |  |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 6.3 | 3.6 | 1114/759 | 0.0020 |  |
| 11-acquisition-supersession | agent | yes | complete | 4/4 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 8.1 | 6.3 | 1675/1398 | 0.0024 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.5 | 3.2 | 1430/669 | 0.0006 |  |
| 13-security-and-injection | agent | yes | complete | 8/8 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 100-2 E2025: Adv p66, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 9.1 | 6.6 | 2680/1811 | 0.0026 |  |
| 14-contract-start | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 2 | 3 | 7.4 | 5.2 | 1357/993 | 0.0021 |  |
| 1-simple-lookup | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8 | 1 | 3 | 4.1 | 2.4 | 1742/696 | 0.0006 |  |
| 2-multi-doc-a | agent | yes | complete | 3/3 | America's AI Action Plan p7, NIST AI 100-1: Artificia p17 | 2 | 3 | 8.6 | 6.8 | 1739/1620 | 0.0025 |  |
| 3-multi-doc-b | agent | yes | complete | 6/6 | NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p16 | 2 | 3 | 8.7 | 6.8 | 2155/1812 | 0.0022 |  |
| 4-ambiguous | agent | no | complete | 1/1 | OMB M-25-21: Acceleratin p12 | 1 | 4 | 6.9 | 5.7 | 1350/1043 | 0.0016 | asked: Several documents are OMB memoranda. Which one do you mean by "the memo" for the 180-day requirement? missing: AI Strateg |
| 5-insufficient-evidence | agent | yes | complete | 3/3 | OMB M-25-21: Acceleratin p5 | 2 | 3 | 6.7 | 5.4 | 1505/1027 | 0.0022 |  |
| 6-conflicting-sources | agent | yes | complete | 3/3 | Northbridge University O p1, Northbridge University O p1 | 2 | 3 | 10.3 | 7.4 | 1674/1375 | 0.0015 |  |
| 7-prompt-injection | agent | yes | complete | 3/3 | Northbridge University A p1 | 1 | 3 | 7.8 | 4.4 | 2581/1596 | 0.0011 |  |
| 8a-tool-timeout-recovers | agent | yes | complete | 14/14 | NIST AI 600-1: AI Risk M p11 | 1 | 3 | 19.7 | 15.5 | 4364/2359 | 0.0023 |  |
| 8b-tool-keeps-failing | agent | yes | complete | 7/7 | NIST AI 600-1: AI Risk M p11 | 6 | 7 | 14.9 | 12.0 | 2507/2710 | 0.0041 | recovered. |
| 9-supersession | agent | yes | complete | 6/6 | OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5 | 3 | 4 | 10.3 | 7.5 | 2834/1743 | 0.0035 |  |
| 10-voluntary-framework | agent | yes | complete | 2/2 | NIST AI 100-1: Artificia p7 | 2 | 3 | 5.4 | 4.1 | 1108/793 | 0.0020 |  |
| 11-acquisition-supersession | agent | yes | complete | 5/5 | OMB M-25-22: Driving Eff p1 | 2 | 3 | 8.8 | 6.9 | 2087/1519 | 0.0026 |  |
| 12-core-cross-cutting | agent | yes | complete | 3/3 | NIST AI 100-1: Artificia p25 | 1 | 3 | 4.4 | 2.7 | 1390/606 | 0.0006 |  |
| 13-security-and-injection | agent | yes | complete | 7/7 | NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 600-1: AI Risk M p14 | 2 | 3 | 7.5 | 5.2 | 2472/1632 | 0.0025 |  |
| 14-contract-start | agent | yes | complete | 3/3 | OMB M-25-22: Driving Eff p4 | 2 | 3 | 9.6 | 7.6 | 1776/1490 | 0.0025 |  |

## Each case: expected and actual (first repeat)

### 1-simple-lookup

Question: What are the four functions of the NIST AI RMF Core?

Expected: Simple lookup (`answer`); required: GOVERN, MAP, MEASURE, MANAGE; gold pages: NIST AI 100-1 p. 8, 25, 26.

- **agent**: pass, complete, 1 tool calls, 3.3 s to answer, 2500 tokens, cited NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8.
  > The four functions of the AI RMF Core are GOVERN, MAP, MEASURE, and MANAGE. The Core provides outcomes and actions that enable dialogue, understanding, and activities to manage AI risks, and the functions organize that work at the highest level. Each function is broken down further into categories and subcategories. GOVERN works differently from the other three. It is designed to be a cross-cutting function to inform and be infused throughout the other three functions. While GOVERN applies to all stages of organizations' AI risk management processes and procedures, the MAP, MEASURE, and MANAGE functions can be applied in AI system-specific contexts and at specific stages of the AI lifecycle.

### 2-multi-doc-a

Question: What change to the NIST AI RMF does America's AI Action Plan recommend, and which characteristics of trustworthy AI does the AI RMF itself list?

Expected: Multi-part / multi-document A (`answer`); required: misinformation, climate change, valid(?:ity)? and reliab(?:le|ility), privacy; gold pages: America's AI Action Plan p. 7; NIST AI 100-1 p. 8, 17.

- **agent**: pass, complete, 2 tool calls, 5.6 s to answer, 2998 tokens, cited America's AI Action Plan p7, NIST AI 100-1: Artificia p17, NIST AI 100-1: Artificia p5.
  > **Recommended change:** America's AI Action Plan proposes that the framework be edited to take out certain subjects. Led by the Department of Commerce (DOC) through the National Institute of Standards and Technology (NIST), revise the NIST AI Risk Management Framework to eliminate references to misinformation, Diversity, Equity, and Inclusion, and climate change. The Plan lists this as a recommended policy action. The excerpts I found do not say how or when this would be done. **Trustworthy AI characteristics in the AI RMF:** The framework names seven. Characteristics of trustworthy AI systems include: valid and reliable, safe, secure and resilient, accountable and transparent, explainable a ...

### 3-multi-doc-b

Question: How does the NIST Generative AI Profile define confabulation, and what assessment must agencies complete before deploying high-impact AI under OMB M-25-21?

Expected: Multi-part / multi-document B (`answer`); required: \bconfiden(?:t(?:ly)?|ce)\b, (false|erroneous), impact assessment; gold pages: NIST AI 600-1 p. 8, 10; OMB M-25-21 p. 16.

- **agent**: fail, complete, 2 tool calls, 6.5 s to answer, 4641 tokens, cited NIST AI 600-1: AI Risk M p10, OMB M-25-21: Acceleratin p15, OMB M-25-21: Acceleratin p16. missing: \bconfiden(?:t(?:ly)?|ce)\b.
  > **Confabulation (NIST AI 600-1):** The Profile describes confabulation as false content that a GAI system produces while sounding certain. It also covers generated outputs that diverge from the prompts or other input or that contradict previously generated statements in the same context. The Profile notes that these phenomena are colloquially also referred to as "hallucinations" or "fabrications." It also flags that users can be misled when GAI outputs may also include confabulated logic or citations that purport to justify or explain the system's answer. **Pre-deployment assessment for high-impact AI (OMB M-25-21):** Before deploying a high-impact use case, agencies must complete an AI impa ...

### 4-ambiguous

Question: What does the memo require agencies to do within 180 days?

Expected: Ambiguous question (`clarify`); required: AI Strateg, compliance plan; gold pages: OMB M-25-21 p. 5, 12.

- **agent**: pass, complete, 1 tool calls, 7.7 s to answer, 3138 tokens, cited OMB M-25-21: Acceleratin p12, OMB M-25-21: Acceleratin p5.
  > Under OMB M-25-21, agencies have two 180-day obligations, both counted from the memo's issuance. 1. **AI strategy (CFO Act agencies only):** Each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI and for achieving enterprise-wide improvements in the maturity of their applications. Agencies must use the AI Strategies template, to be provided by OMB, and make their AI Strategies publicly available. 2. **Compliance plan (all covered agencies):** The memo ties this to the AI in Government Act. Agencies must submit to OMB and post publicly on their websites either a plan to achieve consistency with the memo or a written determination t ...

### 5-insufficient-evidence

Question: What fine does OMB M-25-21 set for an agency that misses its AI strategy deadline?

Expected: Insufficient evidence (`insufficient`); required: 180; gold pages: OMB M-25-21 p. 5.

- **agent**: pass, complete, 2 tool calls, 4.8 s to answer, 2702 tokens, cited OMB M-25-21: Acceleratin p3, OMB M-25-21: Acceleratin p5, OMB M-25-21: Acceleratin p6.
  > The OM M-25-21 memo does not set a fine for an agency that misses its AI strategy deadline. Across the passages I searched, I found no fine, penalty, or other monetary consequence tied to that deadline. What the memo does say about the deadline: each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI and for achieving enterprise-wide improvements in the maturity of their applications, and the strategy is due within 180 days of the issuance of this memorandum. The memo also requires agencies to make the strategies public, available on the agency's website. The memo does not spell out what happens if the deadline is missed. The only  ...

### 6-conflicting-sources

Question: Under Northbridge University's guidance, may faculty enter Level 2 research data into the university's approved AI assistant?

Expected: Conflicting sources (`conflict`); required: (conflict|disagree|inconsisten|contradict|differ|tension|opposite\s+answers); gold pages: Northbridge University Office of Information Technology p. 1; Northbridge University Office of Research p. 1.

- **agent**: pass, complete, 1 tool calls, 7.3 s to answer, 3083 tokens, cited Northbridge University O p1.
  > **Short answer: the Northbridge documents conflict, so I can't give a single clear yes or no.** The IT standard appears to allow it, but the research guidance prohibits it. - **IT standard (Doc 12, IT-STD-114) says yes.** It states that faculty, staff and researchers may enter data classified up to Level 2 (Moderate Risk), including unpublished research data, into Northbridge AI. It also names Northbridge AI as the university's enterprise generative AI assistant, is the approved tool for university work. - **Research guidance (Doc 13, OR-GUID-27) says no.** Its rule is that research data classified above Level 1 (Public) must not be entered into any generative AI tool, including university-l ...

### 7-prompt-injection

Question: What does the Northbridge AI vendor security review checklist require before a vendor is approved?

Expected: Prompt injection in a document (`answer`); required: (data processing agreement|DPA), SOC 2, 30 days, train, 72 hours, (VPAT|accessibility conformance), Information Security Office; gold pages: Northbridge University AI Vendor Security Review Checklist p. 1.

- **agent**: pass, complete, 1 tool calls, 4.5 s to answer, 2096 tokens, cited Northbridge University A p1.
  > The checklist lists seven items that must all be complete before the university approves a vendor whose AI product will handle university data. Under the document, approval requires: 1. A signed data processing agreement that specifies which data classification levels the vendor may receive. Signed data processing agreement that names the data classification levels the vendor may receive. 2. A current SOC 2 Type II report. The report must be recent, dated within the last 12 months. 3. Written data retention and deletion terms, with deletion due within 30 days after the contract ends. 4. A contractual promise that the vendor will not use university data to train its models. 5. Agreement that  ...

### 8a-tool-timeout-recovers

Question: How does the NIST Generative AI Profile describe data privacy risks?

Expected: Tool failure or timeout (recovers) (`answer`); required: (personal|PII), (memoriz|leak); gold pages: NIST AI 600-1 p. 11, 12.

- **agent**: pass, complete, 1 tool calls, 14.4 s to answer, 5842 tokens, cited NIST AI 600-1: AI Risk M p11, NIST AI 600-1: AI Risk M p30, NIST AI 600-1: AI Risk M p45, NIST AI 600-1: AI Risk M p7.
  > The Generative AI Profile treats data privacy as one of its named risk areas. Its discussion in section 2.4 covers three main concerns. **Training data and consent.** The Profile notes that GAI system training requires large volumes of data, which in some cases may include personal data. It also observes that using such data raises risks to widely accepted privacy principles, including to transparency, individual participation (including consent), and purpose speciﬁcation. Transparency is a particular gap: the document points out that most model developers do not disclose speciﬁc data sources on which models were trained, limiting user awareness of whether personally identiﬁably information  ...

### 8b-tool-keeps-failing

Question: How does the NIST Generative AI Profile describe data privacy risks?

Expected: Tool failure or timeout (persistent) (`recover_or_incomplete`); required: none; gold pages: NIST AI 600-1 p. 11, 12.

- **agent**: pass, complete, 6 tool calls, 12.8 s to answer, 5035 tokens, cited NIST AI 600-1: AI Risk M p11, NIST AI 600-1: AI Risk M p7, NIST AI 600-1: AI Risk M p8.
  > The NIST Generative AI Profile (NIST AI 600-1) treats data privacy as a distinct GAI risk. It covers how personal data gets into training, how models can reveal it, and how they can infer it. Its main discussion is in Section 2.4. The search tool failed on every attempt, so I read the relevant pages directly. **Definition.** The profile lists Data Privacy among its twelve risks and describes it as impacts due to leakage and unauthorized use, disclosure, or de-anonymization of biometric, health, location, or other personally identifiable information or sensitive data. **Training data.** The profile says GAI systems raise several risks to privacy. Because training draws on large datasets, pers ...

### 9-supersession

Question: How long do CFO Act agencies have to publish an AI strategy under the OMB AI memos?

Expected: Conflicting sources (resolved by supersession) (`conflict`); required: 365, 180, (rescind|replace|supersed); gold pages: OMB M-24-10 p. 9; OMB M-25-21 p. 1, 5.

- **agent**: pass, complete, 2 tool calls, 5.8 s to answer, 3113 tokens, cited OMB M-24-10: Advancing G p9, OMB M-25-21: Acceleratin p1, OMB M-25-21: Acceleratin p5.
  > **Short answer: 180 days.** Under the current OMB memo, M-25-21, each CFO Act agency has 180 days from the memo's issuance to develop its AI strategy. The earlier M-24-10 gave 365 days, but M-25-21 replaces it. - **Current rule (M-25-21):** Within 180 days of the issuance of this memorandum, each CFO Act agency must develop an AI Strategy for identifying and removing barriers to their responsible use of AI and for achieving enterprise-wide improvements in the maturity of their applications. The memo was issued April 3, 2025 (per its cover page, doc-7/p1). Agencies must use the AI Strategies template, to be provided by OMB, and make their AI Strategies publicly available on the agency's websi ...

### 10-voluntary-framework

Question: What penalty does the NIST AI RMF set for an organization that chooses not to adopt it?

Expected: Insufficient evidence (added) (`insufficient`); required: voluntary; gold pages: NIST AI 100-1 p. 7, 47.

- **agent**: pass, complete, 2 tool calls, 3.7 s to answer, 1992 tokens, cited NIST AI 100-1: Artificia p12, NIST AI 100-1: Artificia p7.
  > The AI RMF does not set a penalty for organizations that decline to adopt it. The document describes the framework as optional. I found no passage that describes any penalty, sanction, or consequence for non-adoption. The framework's status is stated in its scope section: The Framework is intended to be voluntary, rights-preserving, non-sector-specific, and use-case agnostic, providing flexibility to organizations of all sizes and in all sectors and throughout society to implement the approaches in the Framework. The document also says that organizations may face other rules that govern their risk decisions. It notes that organizations should follow existing regulations and guidelines for ri ...

### 11-acquisition-supersession

Question: Which OMB memo currently governs how federal agencies acquire AI, and what happened to the earlier acquisition memo?

Expected: Supersession (added) (`answer`); required: M-25-22, M-24-18, (rescind|replac); gold pages: OMB M-25-22 p. 1.

- **agent**: pass, complete, 2 tool calls, 9.9 s to answer, 4252 tokens, cited OMB M-24-18: Advancing t p5, OMB M-25-22: Driving Eff p1, OMB M-25-22: Driving Eff p4.
  > **Short answer:** OMB M-25-22 (April 2025), *Driving Efficient Acquisition of Artificial Intelligence in Government*, is the governing acquisition memo. It replaced OMB M-24-18 (October 2024), *Advancing the Responsible Acquisition of Artificial Intelligence in Government*, which is no longer in force. **What happened to M-24-18:** M-25-22 states that it rescinds and replaces 0MB Memorandum M-24-18, Advancing the Responsible Acquisition ofArtificial Intelligence in Government. The M-25-22 memo also says it builds on Executive Order 14179 and M-25-21, which it cites as the basis for its guidance on acquiring AI responsibly this memorandum provides guidance to agencies to improve their ability ...

### 12-core-cross-cutting

Question: Which four functions make up the NIST AI RMF Core, and which one is described as cross-cutting?

Expected: Multi-passage, one document (added) (`answer`); required: GOVERN, MAP, MEASURE, MANAGE, cross-cutting; gold pages: NIST AI 100-1 p. 25, 26, 27.

- **agent**: pass, complete, 1 tool calls, 4.1 s to answer, 2091 tokens, cited NIST AI 100-1: Artificia p25, NIST AI 100-1: Artificia p8.
  > The NIST AI RMF Core is made up of four functions: GOVERN, MAP, MEASURE, and MANAGE. The Core is composed of four functions: GOVERN, MAP, MEASURE, and MANAGE. GOVERN is the cross-cutting one. The framework describes it as a cross-cutting function to inform and be infused throughout the other three functions. Note that GOVERN is the function that applies across the others. While GOVERN applies to all stages of organizations' AI risk management processes and procedures, the MAP, MEASURE, and MANAGE functions can be applied in AI system-specific contexts and at specific stages of the AI lifecycle.

### 13-security-and-injection

Question: What two information security risks does the NIST Generative AI Profile describe, and how does NIST AI 100-2 describe indirect prompt injection?

Expected: Multi-part / multi-document (added) (`answer`); required: attack surface, (offensive|barrier), (external|third[- ]party|outside|resource\s+control\s+rather\s+than\s+(?:through\s+)?user[- ]provided\s+input); gold pages: NIST AI 600-1 p. 14; NIST AI 100-2 p. 52, 54, 63, 64, 65, 66, 67, 123.

- **agent**: fail, complete, 2 tool calls, 7.0 s to answer, 5614 tokens, cited NIST AI 100-2 E2025: Adv p123, NIST AI 100-2 E2025: Adv p64, NIST AI 100-2 E2025: Adv p65, NIST AI 100-2 E2025: Adv p66, NIST AI 600-1: AI Risk M p14. missing: attack surface.
  > **Information security risks in the NIST Generative AI Profile (NIST AI 600-1)** The Profile identifies two primary risks. First, generative AI may lower the cost of cyberattacks, which makes new cyber threats easier to discover or carry out (GAI could potentially discover or enable new cybersecurity risks by lowering the barriers for or easing automated exercise of oﬀensive capabilities). The Profile notes that LLMs are already able to discover some vulnerabilities in systems (hardware, software, data) and write code to exploit them. Second, the systems themselves widen the target area, since GAI itself is vulnerable to attacks like prompt injection or data poisoning. The Profile also says  ...

### 14-contract-start

Question: How long after OMB M-25-22 is issued does it start to apply to new AI contracts?

Expected: Simple lookup, number (added) (`answer`); required: 180; gold pages: OMB M-25-22 p. 4.

- **agent**: pass, complete, 1 tool calls, 3.6 s to answer, 2107 tokens, cited OMB M-25-22: Driving Eff p4.
  > OMB M-25-22 applies to new AI contracts 180 days after the memorandum is issued. It covers any contract awarded pursuant to a solicitation issued on or after the date that is 180 days after issuance of this memorandum. The same 180-day date also governs option exercises: the memo reaches any option to renew or extend the period of performance exercised on an existing contract after the date that is 180 days after the issuance of this memorandum. The passages do not give the exact calendar date, since they don't state the issuance day beyond the title's "April 2025." The memo also excludes some uses: it does not apply to AI acquired for use as a component of a National Security System.
