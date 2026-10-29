"""Ask a question from the command line and print the answer with its checked citations.

    python scripts/ask.py "What are the four functions of the AI RMF Core?" [--mode baseline]

Creates a session (the API sets its cookie), starts a run, follows it until it ends, then
prints the answer, each citation with its document, page and provenance check, and the totals.
Standard library only.
"""

import argparse
import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.request
import uuid


class Client:
    def __init__(self, base: str) -> None:
        self.base = base
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )

    def call(self, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        req = urllib.request.Request(self.base + path, data=body, method=method, headers=headers)
        try:
            with self.opener.open(req, timeout=60) as resp:
                return resp.status, json.loads(resp.read() or b"null")
        except urllib.error.HTTPError as err:
            return err.code, error_body(err)


def error_body(err: urllib.error.HTTPError):
    """The API's JSON error, or, from a proxy's HTML error page, its first line as the detail."""
    raw = err.read() or b"null"
    try:
        return json.loads(raw)
    except ValueError:
        return {"detail": raw.decode(errors="replace").strip().splitlines()[0][:200]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--mode", default="agent", choices=["agent", "baseline"])
    parser.add_argument("--reply", help="answer to send if the agent asks a clarifying question")
    parser.add_argument(
        "--fault",
        action="append",
        default=[],
        metavar="TOOL=MODE",
        help="inject a tool failure (needs ALLOW_FAULT_INJECTION=true), "
        "e.g. search_documents=timeout",
    )
    parser.add_argument("--base", default="http://localhost:8080")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    client = Client(args.base)
    _, session = client.call("POST", "/api/sessions")
    payload = {"question": args.question, "mode": args.mode}
    if args.fault:
        if any("=" not in f for f in args.fault):
            parser.error("--fault must use the form TOOL=MODE")
        payload["faults"] = dict(f.split("=", 1) for f in args.fault)
    status, run = client.call("POST", f"/api/sessions/{session['id']}/runs", payload)
    if status != 202:
        print("ask failed:", status, run)
        return 1

    started = time.monotonic()
    while run["status"] == "running" and time.monotonic() - started < args.timeout:
        time.sleep(1)
        _, run = client.call("GET", f"/api/runs/{run['id']}")
        if run["status"] == "needs_clarification":
            asked = [e["data"] for e in run["events"] if e["type"] == "clarification"][-1]
            print(f"agent asks: {asked['question']}  options: {asked['options']}")
            if not args.reply:
                break
            print(f"replying: {args.reply}")
            body = {
                "tool_use_id": asked["tool_use_id"],
                "idempotency_key": uuid.uuid4().hex,
                "reply": args.reply,
            }
            status, run = client.call(
                "POST", f"/api/sessions/{session['id']}/runs/{run['id']}/resume", body
            )
            if status != 202:
                print("resume failed:", status, run)
                return 1
            args.reply = None  # answer one clarification

    print(f"status: {run['status']}  {run.get('status_reason') or ''}")
    for event in run.get("events", []):
        data = event["data"]
        if event["type"] in ("clarification", "clarification_answered", "limit"):
            print(f"  {event['type']}: {json.dumps(data)}")
        elif event["type"] == "tool_call":
            retried = f", retried after {data['retries']}" if data.get("retries") else ""
            print(
                f"  tool {data['tool']} {json.dumps(data['input'])} -> {data['status']}, "
                f"{data.get('summary', '')}, cache {data.get('cache')}, {data.get('ms')} ms"
                f"{retried}"
            )
        elif event["type"] == "model_call":
            print(
                f"  model turn {data['turn']} ({data['purpose']}): {data['ms']} ms, "
                f"in {data['input_tokens']} out {data['output_tokens']} tokens, "
                f"${data['cost_usd']:.4f}, stop {data['stop_reason']}"
            )
    answer = run.get("answer")
    if answer:
        text = "".join(
            seg["text"] + "".join(f"[{n}]" for n in seg["citations"]) for seg in answer["segments"]
        )
        print("\n" + text + "\n")
        for c in answer["citations"]:
            print(
                f"[{c['number']}] {c['title']} (doc {c['document_id']}, page {c['page_no']}) "
                f'{c["provenance"]}: "{c["cited_text"][:120]}"'
            )
    finished = [e["data"] for e in run.get("events", []) if e["type"] == "run_finished"]
    if finished:
        f = finished[-1]
        print(
            f"\ntotals: {f.get('ms')} ms, {f.get('model_calls')} model calls, "
            f"{f.get('tool_calls')} tool calls, ${f.get('cost_usd', 0):.4f}"
        )
    return 0 if run["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
