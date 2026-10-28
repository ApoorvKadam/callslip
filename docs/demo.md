# Walkthrough

A reproducible walkthrough of the four behaviours the brief asks to see: a multi-document question, evidence-driven re-retrieval, a clarification, and a failed tool call. Each step has the command or UI action, what happens, and a saved trace from the committed evaluation run.

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

Selecting a citation number highlights the text it supports and opens its source: the quote, the page check ("Quote found on page 7") and a link to the PDF page (Action Plan p. 7, AI RMF p. 17). Text that the answer copies word for word from a source is shown in quotation marks.

![The same answer with its steps](images/2-steps.png)

The Steps tab shows the plan the model chose: it listed the documents, searched once in each document (`search_documents` with a `document_ids` filter), then answered. Each model turn shows its tokens and cost, and the run's totals close the list.

Saved trace: [`2-multi-doc-a.agent.1.json`](../eval/results/2026-10-28T043802Z/traces/2-multi-doc-a.agent.1.json). The single-pass baseline on the same question ([`2-multi-doc-a.baseline.1.json`](../eval/results/2026-10-28T043802Z/traces/2-multi-doc-a.baseline.1.json)) only retrieved AI RMF passages and said it could not answer the Action Plan part.

## 2. Evidence-driven re-retrieval

```bash
python3 scripts/ask.py "How does the NIST Generative AI Profile describe data privacy risks?" \
  --fault search_documents=error
```

Search fails on every call (injected below the cache; the server must run with `ALLOW_FAULT_INJECTION=true`). The run's steps show the agent change its plan based on what came back: it checks the document list, a first search fails after its retry, a rewritten search filtered to the Profile fails too, and it switches to `read_document_section`. It reads pages 5 to 7, 8 to 10 and 11 to 12 until it reaches section 2.4 Data Privacy, then answers with citations from pages 8 and 11 and says the search was unavailable.

Saved trace: [`8b-tool-keeps-failing.agent.1.json`](../eval/results/2026-10-28T043802Z/traces/8b-tool-keeps-failing.agent.1.json).

Without faults, the same pattern shows up on smaller scales: after `list_documents` the agent narrows each search to the right document ([`3-multi-doc-b.agent.1.json`](../eval/results/2026-10-28T043802Z/traces/3-multi-doc-b.agent.1.json)), and for the conflicting-policy question, after finding both policies, it searches once more for a statement of which one takes precedence, then says there is none ([`6-conflicting-sources.agent.1.json`](../eval/results/2026-10-28T043802Z/traces/6-conflicting-sources.agent.1.json)).

## 3. Clarification

Ask: *What does the memo require agencies to do within 180 days?*

![The agent asks which memo](images/3-clarification-asked.png)

The corpus holds four OMB memos, so the agent checks the document list and asks which one, offering each memo as a button. The run is paused (`needs_clarification`). The question box now sends a reply, and the question can also be skipped. Choose M-25-21:

![Answer after the reply](images/4-clarification-answered.png)

The same run continues: the reply becomes the result of the `ask_clarification` call, the agent searches only M-25-21, and answers with both 180-day requirements (AI strategy, p. 5; compliance plan, p. 12). The Steps tab shows the question and the reply as steps of the same run. From a terminal: `python3 scripts/ask.py "What does the memo require agencies to do within 180 days?" --reply "OMB M-25-21"`.

Saved trace: [`4-ambiguous.agent.1.json`](../eval/results/2026-10-28T043802Z/traces/4-ambiguous.agent.1.json).

## 4. Failed tool call with bounded retry

```bash
python3 scripts/ask.py "How does the NIST Generative AI Profile describe data privacy risks?" \
  --fault search_documents=timeout_once
```

The first search times out after 8 seconds; the executor retries once, the retry succeeds, and the search step shows it was retried after "timed out after 8 s", and a normal cited answer follows. With `--fault search_documents=error` (step 2) the retry also fails and the failure goes back to the model as a typed error.

Saved trace: [`8a-tool-timeout-recovers.agent.1.json`](../eval/results/2026-10-28T043802Z/traces/8a-tool-timeout-recovers.agent.1.json).

## 5. Limits and an incomplete answer

```bash
echo "MAX_TOOL_CALLS=2" >> .env                  # settings come from .env (see runbook)
ALLOW_FAULT_INJECTION=true docker compose up -d --wait api
python3 scripts/ask.py "How does the NIST Generative AI Profile describe data privacy risks?" --fault search_documents=error
sed -i '/^MAX_TOOL_CALLS=/d' .env && ALLOW_FAULT_INJECTION=true docker compose up -d --wait api   # back to the defaults
```

The second tool call reaches the limit. The steps show the limit, then one final model call with tools disabled writes the best answer from the evidence so far. Here there is none, so it says it cannot answer and why, without answering from memory. The run ends `incomplete` with "the limit of 2 tool calls was reached". If the model asks for a tool after a limit, that call is not run and the model is told why.

## 6. Redis outage

```bash
docker compose stop redis
python3 scripts/ask.py "What are the four functions of the NIST AI RMF Core?"
docker compose start redis
```

The answer is unchanged; the search steps show "cache unavailable", and `/api/ready` reports `degraded` until Redis is back.
