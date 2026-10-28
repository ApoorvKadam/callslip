# Support check against hand labels, 2026-10-28T152456Z

Judge: `claude-haiku-5-5`, the prompt and schema in `backend/app/agent/support.py`.

| Pieces | Hand label | Judge: supported | Judge: partly | Judge: not supported | Not checked |
|---|---|---|---|---|---|
| altered | not_supported | 0 | 0 | 12 | 0 |
| altered | partly | 0 | 2 | 0 | 0 |
| real | supported | 55 | 5 | 0 | 0 |
| swapped | not_supported | 1 | 0 | 9 | 0 |

Labelled partly or not supported but judged supported: 1 of 24.
Labelled supported but not judged supported: 5 of 60.

## Judged supported, labelled otherwise

- `swapped-13-16` (supported): the intended purpose for the AI and its expected benefit, supported by specific metrics or qualitative analysis | Passage lists intended purpose and expected benefit supported by specific metrics or qualitative analysis.

## Labelled supported, judged otherwise

- `real-19` (partly): Agencies must use the AI Strategies template, to be provided by OMB, and make their AI Strategies publicly | Passage says agencies must use the OMB template and make strategies publicly available, but the 'publicly' phrase is cut off; the rest is mostly unrelated text.
- `real-25` (partly): must use the AI Strategies template, to be provided by 0MB, and make their AI Strategies publicly | Passage confirms agencies must use the template from OMB and make strategies public, but the 'strategies' reference beyond that is not in the passage.
- `real-48` (partly): use of proprietary or sensitive training data is consistent with applicable laws. | Passage says diligence should examine whether sensitive training data use is consistent with laws, not that it is consistent.
- `real-58` (partly): 365 days of the issuance of this memorandum | Passage says 365 days for a strategy to be developed and released publicly, but the claim is just a fragment and the date-of-deadline calculation is not in the passage.
- `real-59` (partly): This memorandum rescinds and replaces Office of Management and Budget (0MB) Memorandum M-24-10, Advancing Governance, Innovation, and Risk M | Passage confirms M-24-10 is rescinded and replaced, but does not mention the 'Advancing Governance' title as a memo being rescinded beyond that; the replacement is stated, so mostly consistent.
