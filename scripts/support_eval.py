"""How well does the support check judge? Compare it with hand labels.

    ANTHROPIC_API_KEY=... uv run --project backend python scripts/support_eval.py

Reads eval/support_check/labels.json: cited pieces of saved answers with their quotes and a hand
label, plus pieces altered by hand (a changed number or rule) and pieces paired with a quote
about something else. Sends them to the judge exactly as a run does (the prompt, schema and
reply handling in backend/app/agent/support.py), one call per case, and writes report.md and
results.json next to the labels. A piece labelled partly or not supported that the judge calls
supported is the error that matters: it would tell a reader a quote backs a sentence it does not.
"""

import argparse
import asyncio
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from anthropic import AsyncAnthropic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.agent.support import SCHEMA, SUPPORT_SYSTEM, request, verdicts  # noqa: E402

FOLDER = ROOT / "eval" / "support_check"


async def judge(client: AsyncAnthropic, model: str, items: list[dict]) -> list[dict]:
    claims = [
        {
            "claim": n,
            "text": it["text"],
            "context": it["context"],
            "quotes": it["quotes"],
            "citations": [],
        }
        for n, it in enumerate(items, start=1)
    ]
    message = await client.messages.create(
        model=model,
        max_tokens=4000,
        system=[{"type": "text", "text": SUPPORT_SYSTEM}],
        messages=request(claims),
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    reply = next((b.text for b in message.content if b.type == "text"), None)
    return verdicts(claims, reply)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="claude-haiku-5-5")
    args = parser.parse_args()

    labels = json.loads((FOLDER / "labels.json").read_text())
    by_case: dict[str, list[dict]] = defaultdict(list)
    for item in labels:
        by_case[item["case"]].append(item)
    client = AsyncAnthropic()
    calls = [judge(client, args.model, items) for items in by_case.values()]
    results = []
    for items, checks in zip(by_case.values(), await asyncio.gather(*calls), strict=True):
        for item, check in zip(items, checks, strict=True):
            results.append({**item, "verdict": check["verdict"], "reason": check["reason"]})

    table = Counter((r["kind"], r["label"], r["verdict"]) for r in results)
    false_support = [
        r for r in results if r["label"] != "supported" and r["verdict"] == "supported"
    ]
    missed = [r for r in results if r["label"] == "supported" and r["verdict"] != "supported"]
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    lines = [
        f"# Support check against hand labels, {stamp}",
        "",
        f"Judge: `{args.model}`, the prompt and schema in `backend/app/agent/support.py`.",
        "",
        "| Pieces | Hand label | Judge: supported | Judge: partly | Judge: not supported "
        "| Not checked |",
        "|---|---|---|---|---|---|",
    ]
    for kind, label in sorted({(r["kind"], r["label"]) for r in results}):
        counts = [table[(kind, label, v)] for v in VERDICT_ORDER]
        lines.append(f"| {kind} | {label} | " + " | ".join(map(str, counts)) + " |")
    lines += [
        "",
        f"Labelled partly or not supported but judged supported: {len(false_support)} "
        f"of {sum(r['label'] != 'supported' for r in results)}.",
        f"Labelled supported but not judged supported: {len(missed)} "
        f"of {sum(r['label'] == 'supported' for r in results)}.",
        "",
    ]
    for title, rows in (
        ("Judged supported, labelled otherwise", false_support),
        ("Labelled supported, judged otherwise", missed),
    ):
        if rows:
            lines += [f"## {title}", ""]
            lines += [
                f"- `{r['id']}` ({r['verdict']}): {r['text'][:140]} | {r['reason']}" for r in rows
            ]
            lines.append("")
    (FOLDER / "report.md").write_text("\n".join(lines))
    (FOLDER / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    print("\n".join(lines))
    return 0


VERDICT_ORDER = ("supported", "partly", "not_supported", "not_checked")

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
