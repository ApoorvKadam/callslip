"""Repeatable evaluation: the agent against the single-pass baseline, same corpus, model,
retriever and answer rules. Drives the running stack over HTTP, exactly like a user.

    ALLOW_FAULT_INJECTION=true docker compose up -d --wait   # the tool-failure cases need it
    python3 scripts/load_corpus.py
    python3 scripts/eval.py [--systems agent,baseline] [--repeat 1] [--cases ID,...] [--budget 5]
    python3 scripts/eval.py --rescore eval/results/<run>   # grade saved answers again, no calls

Writes eval/results/<UTC timestamp>/: results.json (every measurement), report.md (tables and
failure notes) and traces/ (each run as the API returns it: steps, answer, citations).

Checks are deterministic and listed per case in eval/cases.json: required facts (patterns),
forbidden content, citation provenance (each quote found on its page), gold pages cited, key
pages cited (the page that settles the question), documents covered, and the expected
behaviour (answer, ask for clarification, say evidence is missing, surface a conflict, recover
from or stop on a tool failure). Whether a quote supports its claim is reviewed by hand; the
report leaves room for that note.
"""

import argparse
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ask import Client  # noqa: E402 - shared HTTP client next to this script

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "eval" / "cases.json"
ASKED_IN_TEXT = re.compile(
    r"(which (one|memo|document|of these)|do you mean|could you clarify)", re.I
)


def wait(client: Client, run: dict, timeout: int) -> dict:
    started = time.monotonic()
    while run["status"] == "running" and time.monotonic() - started < timeout:
        time.sleep(1)
        _, run = client.call("GET", f"/api/runs/{run['id']}")
    _, run = client.call("GET", f"/api/runs/{run['id']}")
    return run


def ask(client: Client, session: str, question: str, mode: str, faults: dict | None) -> dict:
    payload = {"question": question, "mode": mode}
    if faults:
        payload["faults"] = faults
    status, run = client.call("POST", f"/api/sessions/{session}/runs", payload)
    if status != 202:
        raise RuntimeError(f"ask failed: {status} {run}")
    return run


def run_case(client: Client, case: dict, mode: str, timeout: int) -> dict:
    """Run one case in a fresh session. Returns the final run plus how it got there."""
    _, session = client.call("POST", "/api/sessions")
    sid = session["id"]
    run = wait(client, ask(client, sid, case["question"], mode, case.get("faults")), timeout)
    record = {"runs": [run], "clarified": False, "asked_in_text": False}

    if run["status"] == "needs_clarification":
        record["clarified"] = True
        asked = [e["data"] for e in run["events"] if e["type"] == "clarification"][-1]
        record["clarification"] = {"question": asked["question"], "options": asked["options"]}
        body = {
            "tool_use_id": asked["tool_use_id"],
            "idempotency_key": f"eval-{run['id']}",
            "reply": case.get("reply", "Please answer for all of them."),
        }
        status, resumed = client.call("POST", f"/api/sessions/{sid}/runs/{run['id']}/resume", body)
        if status != 202:
            raise RuntimeError(f"resume failed: {status} {resumed}")
        run = wait(client, resumed, timeout)
        record["runs"] = [run]
    elif case["expect"] == "clarify" and case.get("reply"):
        # The baseline cannot pause; it answers or asks in text. Then the user's reply comes as
        # a follow-up question in the same session, which carries the first answer as context.
        text = (run.get("answer") or {}).get("text", "")
        record["asked_in_text"] = bool(ASKED_IN_TEXT.search(text))
        follow_up = f"{case['question']} I mean {case['reply']}."
        run = wait(client, ask(client, sid, follow_up, mode, None), timeout)
        record["runs"].append(run)
    record["final"] = run
    return record


def after_answer_ms(run: dict) -> int:
    """How long a run went on after its answer event: the support check."""
    at = {e["type"]: e["created_at"] for e in run["events"] if "created_at" in e}
    if "answer" not in at or "run_finished" not in at:
        return 0
    gap = datetime.fromisoformat(at["run_finished"]) - datetime.fromisoformat(at["answer"])
    return int(gap.total_seconds() * 1000)


def totals(runs: list[dict]) -> dict:
    out = {
        "ms": 0,
        "model_calls": 0,
        "tool_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cost_usd": 0.0,
    }
    for run in runs:
        finished = [e["data"] for e in run["events"] if e["type"] == "run_finished"]
        f = finished[-1] if finished else {}
        out["ms"] += run.get("exec_ms") or f.get("ms", 0)
        for key in ("model_calls", "input_tokens", "output_tokens", "cache_read_tokens"):
            out[key] += f.get(key, 0)
        out["tool_calls"] += sum(1 for e in run["events"] if e["type"] == "tool_call")
        out["cost_usd"] += f.get("cost_usd", 0.0)
    out["cost_usd"] = round(out["cost_usd"], 5)
    # Time to answer: the total less what came after each run's answer (the support check),
    # measured from event times, so older saved runs can be measured the same way.
    out["answer_ms"] = None
    if runs and any(e["type"] == "answer" for e in runs[-1]["events"]):
        out["answer_ms"] = out["ms"] - sum(after_answer_ms(run) for run in runs)
    out["models"] = sorted(
        {e["data"].get("model") for r in runs for e in r["events"] if e["type"] == "model_call"}
        - {None}
    )
    return out


def score(case: dict, record: dict, titles: dict[int, str]) -> dict:
    run = record["final"]
    answer = run.get("answer") or {"text": "", "citations": []}
    text = answer["text"]
    citations = answer["citations"]
    verified = sum(c["provenance"] == "verified" for c in citations)

    def ids(prefix: str) -> set[int]:
        return {i for i, t in titles.items() if t.startswith(prefix)}

    gold = {(i, p) for g in case["gold"] for i in ids(g["doc"]) for p in g["pages"]}
    cited = {(c["document_id"], c["page_no"]) for c in citations}
    docs_cited = {d for d, _ in cited & gold}  # documents with one of their gold pages cited
    events = [e for r in record["runs"] for e in r["events"]]
    tool_events = [e["data"] for e in events if e["type"] == "tool_call"]
    retrieved = {ev["title"] for t in tool_events for ev in t.get("evidence", [])}

    missing = [p for p in case.get("required", []) if not re.search(p, text, re.I)]
    forbidden = [p for p in case.get("forbidden", []) if re.search(p, text, re.I)]
    checks: dict[str, bool] = {
        "required_facts": not missing,
        "no_forbidden_content": not forbidden,
        "citations_verified": verified == len(citations),
    }
    expect = case["expect"]
    if expect in ("answer", "clarify", "conflict", "insufficient"):
        checks["completed"] = run["status"] == "complete"
        checks["gold_page_cited"] = bool(cited & gold)
    if case.get("must_cite"):
        key = {(i, p) for g in case["must_cite"] for i in ids(g["doc"]) for p in g["pages"]}
        checks["key_pages_cited"] = bool(key) and key <= cited
    if case.get("min_documents"):
        checks["documents_covered"] = len(docs_cited) >= case["min_documents"]
    if expect == "clarify":
        checks["asked_for_clarification"] = record["clarified"] or record["asked_in_text"]
    if expect == "insufficient":
        checks["says_evidence_missing"] = bool(re.search(case["insufficient_pattern"], text, re.I))
    if case.get("must_retrieve"):
        checks["injected_page_reached_model"] = any(
            t.startswith(case["must_retrieve"]) for t in retrieved
        )
    if case.get("expect_retry"):
        checks["retried_after_failure"] = any(
            t.get("retries") and t.get("tool") in case.get("faults", {}) for t in tool_events
        )
    outcome = None
    if expect == "recover_or_incomplete":
        recovered = run["status"] == "complete" and verified > 0 and bool(cited & gold)
        stopped = run["status"] == "incomplete" and bool(run.get("status_reason"))
        outcome = "recovered" if recovered else "stopped within limits" if stopped else "neither"
        checks["recovered_or_reported_incomplete"] = outcome != "neither"
        # Recovering or stopping only counts if the injected fault was actually hit.
        checks["fault_exercised"] = any(
            t.get("tool") in case.get("faults", {}) and t.get("status") in ("error", "timeout")
            for t in tool_events
        )

    failed = [name for name, ok in checks.items() if not ok]
    notes = []
    if missing:
        notes.append(f"missing: {', '.join(missing)}")
    if forbidden:
        notes.append(f"forbidden content: {', '.join(forbidden)}")
    shown = ("required_facts", "no_forbidden_content")  # already named in the notes above
    notes += [f"failed check: {name}" for name in failed if name not in shown]
    if run.get("status_reason"):
        notes.append(f"status reason: {run['status_reason']}")
    return {
        "passed": not failed,
        "checks": checks,
        "outcome": outcome,
        "status": run["status"],
        "citations": len(citations),
        "citations_verified": verified,
        "gold_pages_cited": sorted(f"{titles.get(d, d)[:24]} p{p}" for d, p in cited & gold),
        "documents_cited": len({c["document_id"] for c in citations}),
        "clarification": record.get("clarification"),
        "asked_in_text": record["asked_in_text"],
        "notes": notes,
        **totals(record["runs"]),
    }


def report(results: list[dict], systems: list[str], started: str) -> str:
    lines = [f"# Evaluation results, {started}", ""]
    lines += [
        "| System | Cases passed | Mean latency (s) | Median time to answer (s) "
        "| Mean tool calls | Mean model calls | Citations verified | Total tokens "
        "| Total cost (USD) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for system in systems:
        rows = [r for r in results if r["system"] == system]
        if not rows:
            continue
        cites = sum(r["citations"] for r in rows)
        answered = [r["answer_ms"] for r in rows if r.get("answer_ms") is not None]
        lines.append(
            f"| {system} | {sum(r['passed'] for r in rows)} of {len(rows)} "
            f"| {sum(r['ms'] for r in rows) / len(rows) / 1000:.1f} "
            f"| {median(answered) / 1000 if answered else 0:.1f} "
            f"| {sum(r['tool_calls'] for r in rows) / len(rows):.1f} "
            f"| {sum(r['model_calls'] for r in rows) / len(rows):.1f} "
            f"| {sum(r['citations_verified'] for r in rows)} of {cites} "
            f"| {sum(r['input_tokens'] + r['output_tokens'] for r in rows)} "
            f"| {sum(r['cost_usd'] for r in rows):.4f} |"
        )
    lines += [
        "",
        "| Case | System | Pass | Status | Citations (verified/total) | Gold pages cited "
        "| Tools | Model calls | Latency (s) | To answer (s) | Tokens in/out | Cost (USD) "
        "| Notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        notes = "; ".join(r["notes"]) or ""
        if r["outcome"]:
            notes = f"{r['outcome']}. {notes}".strip()
        if r["clarification"]:
            notes = f"asked: {r['clarification']['question']} {notes}".strip()
        to_answer = "-" if r.get("answer_ms") is None else f"{r['answer_ms'] / 1000:.1f}"
        lines.append(
            f"| {r['case']} | {r['system']} | {'yes' if r['passed'] else 'no'} | {r['status']} "
            f"| {r['citations_verified']}/{r['citations']} | {', '.join(r['gold_pages_cited'])} "
            f"| {r['tool_calls']} | {r['model_calls']} | {r['ms'] / 1000:.1f} "
            f"| {to_answer} "
            f"| {r['input_tokens']}/{r['output_tokens']} | {r['cost_usd']:.4f} | {notes} |"
        )
    return "\n".join(lines) + "\n"


def write(out_dir: Path, meta: dict, results: list[dict]) -> None:
    (out_dir / "results.json").write_text(json.dumps({**meta, "results": results}, indent=1))
    (out_dir / "report.md").write_text(report(results, meta["systems"], meta["started"]))


def rescore(out_dir: Path, titles: dict[int, str]) -> int:
    """Grade a saved run again with the current cases.json, e.g. after a check is corrected."""
    meta = json.loads((out_dir / "results.json").read_text())
    cases = {c["id"]: c for c in json.loads(CASES.read_text())["cases"]}
    results = []
    for old in meta.pop("results"):
        name = f"{old['case']}.{old['system']}.{old['repeat']}.json"
        record = json.loads((out_dir / "traces" / name).read_text())
        scored = score(cases[old["case"]], record, titles)
        scored.update({k: old[k] for k in ("case", "category", "system", "repeat")})
        results.append(scored)
        if scored["passed"] != old["passed"]:
            print(
                f"{name}: {'PASS' if old['passed'] else 'FAIL'} -> "
                f"{'PASS' if scored['passed'] else 'FAIL'} {'; '.join(scored['notes'])}"
            )
    meta["rescored"] = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    write(out_dir, meta, results)
    for system in meta["systems"]:
        rows = [r for r in results if r["system"] == system]
        print(f"{system}: {sum(r['passed'] for r in rows)} of {len(rows)} passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8080")
    parser.add_argument("--systems", default="agent,baseline")
    parser.add_argument("--cases", help="comma-separated case ids (default: all)")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--budget", type=float, default=5.0, help="stop above this cost (USD)")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--rescore", type=Path, help="saved run folder to grade again")
    args = parser.parse_args()

    cases = json.loads(CASES.read_text())["cases"]
    if args.cases:
        wanted = set(args.cases.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    systems = args.systems.split(",")
    client = Client(args.base)
    _, docs = client.call("GET", "/api/documents")
    titles = {d["id"]: d["title"] for d in docs if d["status"] == "ready"}
    if args.rescore:
        return rescore(args.rescore, titles)

    started = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    out_dir = ROOT / "eval" / "results" / started
    out_dir.mkdir(parents=True)  # fails rather than mixing two runs in one folder
    (out_dir / "traces").mkdir()
    results: list[dict] = []
    spent = 0.0
    for repeat in range(1, args.repeat + 1):
        for case in cases:
            for system in systems:
                if spent > args.budget:
                    print(f"budget of ${args.budget} reached; stopping")
                    break
                record = run_case(client, case, system, args.timeout)
                scored = score(case, record, titles)
                scored.update(
                    case=case["id"], category=case["category"], system=system, repeat=repeat
                )
                results.append(scored)
                spent += scored["cost_usd"]
                trace = out_dir / "traces" / f"{case['id']}.{system}.{repeat}.json"
                trace.write_text(json.dumps(record, indent=1, default=str))
                print(
                    f"{case['id']:<28} {system:<9} {'PASS' if scored['passed'] else 'FAIL'} "
                    f"{scored['status']:<12} {scored['ms'] / 1000:5.1f}s "
                    f"tools {scored['tool_calls']} ${scored['cost_usd']:.4f} "
                    f"{'; '.join(scored['notes'])}"
                )

    models = sorted({m for r in results for m in r.get("models", []) if m})
    meta = {"started": started, "systems": systems, "repeat": args.repeat, "models": models}
    write(out_dir, meta, results)
    print(f"\nspent ${spent:.4f}; wrote {out_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
