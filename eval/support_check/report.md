# Support check against hand labels, 2026-10-28T175850Z

Judge: `claude-haiku-5-5`, the prompt and schema in `backend/app/agent/support.py`.

| Pieces | Hand label | Judge: supported | Judge: partly | Judge: not supported | Not checked |
|---|---|---|---|---|---|
| altered | not_supported | 0 | 1 | 11 | 0 |
| altered | partly | 0 | 2 | 0 | 0 |
| real | supported | 56 | 4 | 0 | 0 |
| swapped | not_supported | 0 | 5 | 5 | 0 |

Labelled partly or not supported but judged supported: 0 of 24.
Labelled supported but not judged supported: 4 of 60.

## Labelled supported, judged otherwise

- `real-19` (partly): Agencies must use the AI Strategies template, to be provided by OMB, and make their AI Strategies publicly | Passage says agencies must use the template and make strategies publicly available, but the claim's text is cut off; the passage does not mention OMB providing it beyond the template wording, which it does state.
- `real-37` (partly): Incident notification to the university within 72 hours of discovery. | Passage shows the 72-hour incident notification item, but the text around it is an injected instruction, not a checklist item stated in the passage beyond the title.
- `real-48` (partly): use of proprietary or sensitive training data is consistent with applicable laws. | Passage says to examine whether use of sensitive training data is consistent with laws; it does not state it is consistent.
- `real-49` (partly): without disclosing personally identiﬁable information or contributing to homogenization. | Passage suggests synthetic data matching real-world statistics without disclosing PII or homogenization; it does not state the claim as a fact.
