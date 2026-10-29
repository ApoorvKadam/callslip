"""Write the evaluation runs shown in the app's Evaluation page to frontend/public/evaluation.json.

    python3 scripts/eval_digest.py

It reads the committed results (eval/results/<run>/results.json) and the cases (eval/cases.json)
and keeps what the page shows: per system the totals, per case the question, what was expected
and, for every repeat, the outcome, figures, pages cited and the answer. Run it again after a
run is added or graded again; nothing else writes the file.
"""

import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
RUNS = [
    ("2026-10-28T165727Z", "Recorded comparison: agent and single pass, Claude Haiku 5.5"),
    ("2026-10-28T221200Z", "Final build: agent with each document's outline, Claude Haiku 5.5"),
]


def totals(rows: list[dict]) -> dict:
    answered = [r["answer_ms"] for r in rows if r.get("answer_ms") is not None]
    return {
        "passed": sum(r["passed"] for r in rows),
        "completed": sum(r["status"] == "complete" for r in rows),
        "runs": len(rows),
        "citations": sum(r["citations"] for r in rows),
        "citations_verified": sum(r["citations_verified"] for r in rows),
        "median_answer_ms": median(answered) if answered else None,
        "mean_tool_calls": round(sum(r["tool_calls"] for r in rows) / len(rows), 1),
        "cost_usd": round(sum(r["cost_usd"] for r in rows), 4),
    }


def repeat(r: dict) -> dict:
    return {
        "repeat": r["repeat"],
        "passed": r["passed"],
        "status": r["status"],
        "notes": r["notes"],
        "tool_calls": r["tool_calls"],
        "answer_ms": r.get("answer_ms"),
        "cost_usd": round(r["cost_usd"], 4),
        "cited_pages": r.get("cited_pages", []),
        "answer": r.get("answer", ""),
    }


def digest(run: str, label: str, cases: dict) -> dict:
    meta = json.loads((ROOT / "eval" / "results" / run / "results.json").read_text())
    results = meta["results"]
    order = list(dict.fromkeys(r["case"] for r in results))
    return {
        "run": run,
        "label": label,
        "systems": {s: totals([r for r in results if r["system"] == s]) for s in meta["systems"]},
        "cases": [
            {
                "id": case_id,
                "category": cases[case_id]["category"],
                "question": cases[case_id]["question"],
                "expect": cases[case_id]["expect"],
                "required": cases[case_id].get("required", []),
                "gold": cases[case_id]["gold"],
                "systems": {
                    s: [
                        repeat(r)
                        for r in sorted(results, key=lambda r: r["repeat"])
                        if r["case"] == case_id and r["system"] == s
                    ]
                    for s in meta["systems"]
                },
            }
            for case_id in order
        ],
    }


def main() -> None:
    cases = {c["id"]: c for c in json.loads((ROOT / "eval" / "cases.json").read_text())["cases"]}
    out = ROOT / "frontend" / "public" / "evaluation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps([digest(run, label, cases) for run, label in RUNS], indent=1) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
