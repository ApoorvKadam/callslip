"""Citation checks, replayed against a real recorded answer (tests/fixtures/baseline_run.json).

The fixture holds the exact messages of one single-pass run: passages sent as search_result
blocks, and Claude's answer with its citations. The checks run on that real data, then on
copies with one detail changed, to show each kind of bad citation is caught.
"""

import copy
import json
from pathlib import Path

import pytest

from app.agent.evidence import (
    build_answer,
    check_citation,
    cited_pages,
    collect_evidence,
    parse_source,
    search_result_block,
    source_for,
    text_blocks,
)

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "baseline_run.json").read_text())


@pytest.fixture
def recorded():
    messages = copy.deepcopy(FIXTURE["messages"])
    pages = {(p["document_id"], p["page_no"]): p["text"] for p in FIXTURE["pages"]}
    answer = next(m["content"] for m in messages if m["role"] == "assistant")
    return messages, answer, pages


def first_citation(answer: list[dict]) -> dict:
    return next(c for b in answer for c in (b.get("citations") or []))


def test_every_recorded_citation_is_verified(recorded):
    messages, answer, pages = recorded
    result = build_answer(answer, collect_evidence(messages), pages)
    assert result["citations"], "the recorded answer cites passages"
    assert all(c["provenance"] == "verified" for c in result["citations"])
    assert result["citations_verified"] == len(result["citations"])
    assert {(c["document_id"], c["page_no"]) for c in result["citations"]} == cited_pages(answer)


def test_citations_are_numbered_once_and_attached_to_segments(recorded):
    messages, answer, pages = recorded
    result = build_answer(answer, collect_evidence(messages), pages)
    numbers = [c["number"] for c in result["citations"]]
    assert numbers == list(range(1, len(numbers) + 1))
    used = {n for seg in result["segments"] for n in seg["citations"]}
    assert used == set(numbers)
    assert result["text"] == "".join(seg["text"] for seg in result["segments"])


def test_changed_quote_is_a_text_mismatch(recorded):
    messages, answer, pages = recorded
    citation = first_citation(answer)
    citation["cited_text"] = citation["cited_text"] + " and something the page never said"
    assert check_citation(citation, collect_evidence(messages), pages) == "text_mismatch"


def test_index_beyond_the_evidence_is_unknown(recorded):
    messages, answer, pages = recorded
    citation = first_citation(answer)
    citation["search_result_index"] = 999
    assert check_citation(citation, collect_evidence(messages), pages) == "unknown_index"


def test_source_that_disagrees_with_the_evidence_is_caught(recorded):
    messages, answer, pages = recorded
    citation = first_citation(answer)
    citation["source"] = "doc-1/p2"
    assert check_citation(citation, collect_evidence(messages), pages) == "source_mismatch"


def test_a_repeated_quote_is_checked_again(recorded):
    messages, answer, pages = recorded
    repeat = copy.deepcopy(first_citation(answer))
    repeat["search_result_index"] = 999
    answer.append({"type": "text", "text": " Said again.", "citations": [repeat]})
    result = build_answer(answer, collect_evidence(messages), pages)
    last = result["citations"][result["segments"][-1]["citations"][0] - 1]
    assert last["provenance"] == "unknown_index"
    assert result["citations_verified"] == len(result["citations"]) - 1


def test_quote_missing_from_the_stored_page_is_caught(recorded):
    messages, answer, _ = recorded
    citation = first_citation(answer)
    assert check_citation(citation, collect_evidence(messages), {}) == "not_on_page"


def test_evidence_inside_tool_results_is_numbered_in_order():
    a = search_result_block(1, "A", 2, "First passage.")
    b = search_result_block(3, "B", 4, "Second passage.")
    c = search_result_block(5, "C", 6, "Third passage.")
    messages = [
        {"role": "user", "content": [a, {"type": "text", "text": "q"}]},
        {"role": "assistant", "content": [{"type": "tool_use", "id": "t1"}]},
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "t1", "content": [b, c]}],
        },
    ]
    assert [e.source for e in collect_evidence(messages)] == ["doc-1/p2", "doc-3/p4", "doc-5/p6"]


def test_text_blocks_group_sentences_within_the_limit():
    text = " ".join(f"Sentence {i} is here." for i in range(40))
    blocks = text_blocks(text, max_chars=100)
    assert all(len(b) <= 100 for b in blocks)
    assert " ".join(blocks) == text


def test_source_round_trip():
    assert parse_source(source_for(12, 34)) == (12, 34)
    assert parse_source("https://example.com") is None
