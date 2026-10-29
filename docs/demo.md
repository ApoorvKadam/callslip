# Walkthrough

**Recorded:** [the walkthrough](media/callslip-walkthrough.mp4), made against the local stack. In order, it shows:

| Part | What happens |
|---|---|
| Sign in and upload | A PDF uploaded while signed in is parsed, chunked and embedded, and only that account can see or search it. |
| Two ways to answer | Agent can search again, read pages or ask; Single pass searches once. The line under the question box says which is on. |
| A question across two documents | One search in each document in the same turn, each listed as it happens, the answer as it is written, then each citation's quote on its page. |
| The same question, Single pass | One search over everything. Its passages came from one document, so it said it could not verify the other part. |
| Re-retrieval | The first search finds two different deadlines in two memos, so the agent searches again for which memo replaces the other. |
| Clarification | In a new conversation, "the memo" could be any of four memos, so the agent asks, then answers in the same run. |
| A failed tool call | Search is made to fail (an injected fault). It fails after one retry; the agent takes the document's outline, goes to the section on the topic and reads it. |
| Your own document | A question answered from the private upload, then the upload deleted from the list. |
| Saved conversations | Earlier conversations, with their steps, timing, tokens and cost. |

The recording is scripted with Playwright, so it can be made again after a change. Below, each behaviour the brief asks to see has the command or UI action, what happens, and a saved trace from the committed evaluation run.

Setup (once):

```bash
cp .env.example .env                                   # set POSTGRES_PASSWORD and ANTHROPIC_API_KEY
ALLOW_FAULT_INJECTION=true docker compose up -d --build --wait
python3 scripts/load_corpus.py                         # 14 documents, about 5 minutes on a laptop CPU
```

`scripts/ask.py` prints each run's steps in the terminal. For a question asked in the browser, the same steps are in the Steps tab.

Open http://localhost:8080. The documents are on the left and the conversation is in the middle. The panel on the right belongs to the selected question: Sources lists what its answer cites, and Steps lists each step the agent took.

## 1. Multi-document question

Ask in Agent mode: *What change to the NIST AI RMF does America's AI Action Plan recommend, and which characteristics of trustworthy AI does the AI RMF itself list?*

![A two-document answer with its first source selected](images/1-multi-document.png)

While the agent works, the conversation lists what it is doing ("Choosing where to look", then each search). The answer appears as the model writes it; the line under the question then shows the time to the answer ("Answered in 4.3 s") and "Checking quotes" until the support check is done. Selecting a citation number highlights the text it supports and opens its source: the quote, the page check ("Quote found on page 7"), the support check's verdict ("Supports its sentence") and a link to the PDF page (Action Plan p. 7, AI RMF p. 17). A cited piece of eight or more words that matches its source word for word, apart from spacing and line-break hyphens, is shown in quotation marks.

![The same answer with its steps](images/2-steps.png)

The Steps tab shows the plan the model chose. The first message already lists the documents, so in its first turn it searched once in each document (`search_documents` with a `document_ids` filter), both searches at the same time, then answered. Each model turn shows its time, tokens and cost, and the run's totals close the list.

Saved trace: [`2-multi-doc-a.agent.1.json`](../eval/results/2026-10-28T165727Z/traces/2-multi-doc-a.agent.1.json). The single-pass baseline on the same question ([`2-multi-doc-a.baseline.1.json`](../eval/results/2026-10-28T165727Z/traces/2-multi-doc-a.baseline.1.json)) only retrieved AI RMF passages and said it could not answer the Action Plan part.

The same question in Single pass (switch at the top of the page) does the same in the interface: one search over everything, passages from the AI RMF only, and an answer that says it cannot verify the Action Plan part.

![The same question answered in Single pass](images/6-single-pass.png)

## 2. Evidence-driven re-retrieval

Ask: *How long do CFO Act agencies have to publish an AI strategy under the OMB AI memos?*

The first search, in M-24-10 and M-25-21, finds two different deadlines: 365 days in M-24-10 and 180 days in M-25-21. Nothing in the question asks which memo governs, but the agent searches M-25-21 again for whether it replaces the earlier memo. It finds page 1, "This memorandum rescinds and replaces ... M-24-10", and answers 180 days, citing that page.

Saved trace: [`9-supersession.agent.1.json`](../eval/results/2026-10-28T165727Z/traces/9-supersession.agent.1.json). The single-pass baseline found both deadlines but could not say which one applies, in all three repeats.

The plan also changes when a tool fails:

```bash
python3 scripts/ask.py "How does the NIST Generative AI Profile describe data privacy risks?" \
  --fault search_documents=error
```

Search fails on every call (injected below the cache; the server must run with `ALLOW_FAULT_INJECTION=true`). A search in the Profile fails after its retry; the error says the outline and page reads still work. The agent calls `document_outline`, which lists the Profile's sections from its own bookmarks, finds section 2.4, Data Privacy, on page 11, and reads pages 11 and 12 with `read_document_section`. It answers with citations from those pages and says that search was unavailable.

![Steps of a run whose searches fail](images/5-tool-failure.png)

Saved trace, using the outline: [`8b-tool-keeps-failing.agent.1.json`](../eval/results/2026-10-28T221200Z/traces/8b-tool-keeps-failing.agent.1.json). Before the outline tool, the agent read pages in order instead ([`165727Z`](../eval/results/2026-10-28T165727Z/traces/8b-tool-keeps-failing.agent.1.json)).

## 3. Clarification

Start a new conversation, then ask: *What does the memo require agencies to do within 180 days?*

![The agent asks which memo](images/3-clarification-asked.png)

Four OMB memos in the collection set 180-day deadlines, so the agent asks which one, offering each memo as a button. In the run shown it asked in its first turn, before any search, from the document list alone. The run is paused (`needs_clarification`). The question box now sends a reply, and the question can also be skipped. Choose M-25-21:

![Answer after the reply](images/4-clarification-answered.png)

The same run continues: the reply becomes the result of the `ask_clarification` call, and the agent answers with both 180-day requirements of M-25-21 (AI strategy, p. 5; compliance plan, p. 12). It then searches only M-25-21. The Steps tab shows the question and the reply as steps of the same run. From a terminal: `python3 scripts/ask.py "What does the memo require agencies to do within 180 days?" --reply "OMB M-25-21"`.

In a conversation that already discussed one memo, the same question may not be ambiguous: earlier questions and answers are part of what the agent reads, and it may answer for that memo.

Saved trace: [`4-ambiguous.agent.1.json`](../eval/results/2026-10-28T165727Z/traces/4-ambiguous.agent.1.json). Here the agent asked in its first turn, before any search.

## 4. Failed tool call with bounded retry

```bash
python3 scripts/ask.py "How does the NIST Generative AI Profile describe data privacy risks?" \
  --fault search_documents=timeout_once
```

The first search times out after 8 seconds; the executor retries once, the retry succeeds, and the search step shows it was retried after "timed out after 8 s". A normal cited answer follows (pages 11 and 30). With `--fault search_documents=error` (step 2) the retry also fails and the failure goes back to the model as a typed error.

Saved trace: [`8a-tool-timeout-recovers.agent.1.json`](../eval/results/2026-10-28T165727Z/traces/8a-tool-timeout-recovers.agent.1.json).

## 5. Limits and an incomplete answer

```bash
echo "MAX_TOOL_CALLS=2" >> .env                  # settings come from .env (see runbook)
ALLOW_FAULT_INJECTION=true docker compose up -d --wait api runner   # the runner applies the limits
python3 scripts/ask.py "How does the NIST Generative AI Profile describe data privacy risks?" --fault search_documents=error
sed -i '/^MAX_TOOL_CALLS=/d' .env && ALLOW_FAULT_INJECTION=true docker compose up -d --wait api runner   # back to the defaults
```

The second tool call reaches the limit. The steps show the limit, then one final model call with tools disabled writes the best answer from the evidence so far. Here there is none, so it says it cannot answer and why, without answering from memory. The run ends `incomplete` with "the limit of 2 tool calls was reached". If the model asks for a tool after a limit, that call is not run and the model is told why.

## 6. Redis outage

```bash
docker compose stop redis
python3 scripts/ask.py "What are the four functions of the NIST AI RMF Core?"
docker compose start redis
```

The answer is unchanged; the search steps show "cache unavailable", and `/api/ready` reports `degraded` until Redis is back.
