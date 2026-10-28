"""The evaluation's scoring rules (scripts/eval.py), on hand-made runs: no stack, no model.

Each test is a way an answer could pass without earning it.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import eval as eval_script  # noqa: E402 - scripts/eval.py, not a package

CASES = {c["id"]: c for c in json.loads((ROOT / "eval" / "cases.json").read_text())["cases"]}
TITLES = {1: "OMB M-24-10: Advancing Governance", 2: "OMB M-25-21: Accelerating Federal Use"}


def run(text: str, cited: list[tuple[int, int]]) -> dict:
    citations = [
        {"document_id": d, "page_no": p, "provenance": "verified", "cited_text": "..."}
        for d, p in cited
    ]
    final = {"status": "complete", "events": [], "answer": {"text": text, "citations": citations}}
    return {"runs": [final], "final": final, "clarified": False, "asked_in_text": False}


def score(case_id: str, text: str, cited: list[tuple[int, int]]) -> dict:
    return eval_script.score(CASES[case_id], run(text, cited), TITLES)


def test_an_uncited_deadline_does_not_pass_case_5():
    text = "The memo does not specify a fine. The strategy is due within 180 days."
    assert not score("5-insufficient-evidence", text, [])["passed"]
    assert score("5-insufficient-evidence", text, [(2, 5)])["passed"]


def test_case_9_needs_the_page_that_rescinds_the_older_memo():
    text = "M-24-10 gave 365 days; M-25-21 gives 180 days and replaces it."
    without = score("9-supersession", text, [(1, 9), (2, 5)])
    assert not without["passed"] and not without["checks"]["key_pages_cited"]
    assert score("9-supersession", text, [(1, 9), (2, 5), (2, 1)])["passed"]


def test_each_document_needs_one_of_its_own_gold_pages():
    text = "M-24-10 gave 365 days; M-25-21 gives 180 days and replaces it."
    result = score("9-supersession", text, [(1, 3), (2, 5), (2, 1)])  # p. 3 is not gold
    assert not result["checks"]["documents_covered"]


def test_stopping_counts_for_case_8b_only_after_the_fault_was_hit():
    case = CASES["8b-tool-keeps-failing"]
    record = run("", [])
    record["final"].update(status="incomplete", status_reason="the model call timed out")
    result = eval_script.score(case, record, TITLES)  # no tool was ever called
    assert not result["passed"] and not result["checks"]["fault_exercised"]

    failed = {"tool": "search_documents", "status": "error", "attempts": 2}
    record["final"]["events"] = [{"type": "tool_call", "data": failed}]
    assert eval_script.score(case, record, TITLES)["passed"]
