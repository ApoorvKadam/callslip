"""docs/reproducibility.md quotes the prompts and tool schemas verbatim; keep it that way."""

import json
import re
from pathlib import Path

from app.agent.prompts import AGENT_SYSTEM, BASELINE_SYSTEM
from app.agent.tools import TOOL_DEFINITIONS

DOC = (Path(__file__).resolve().parents[2] / "docs" / "reproducibility.md").read_text()


def block(after: str, lang: str) -> str:
    match = re.search(rf"^{re.escape(after)}.*?```{lang}\n(.*?)\n```", DOC, re.S | re.M)
    assert match, f"no {lang} block after {after!r}"
    return match.group(1)


def test_documented_prompts_are_the_ones_sent():
    assert block("Agent:", "text") == AGENT_SYSTEM
    assert block("Baseline:", "text") == BASELINE_SYSTEM


def test_documented_tool_schemas_are_the_ones_sent():
    assert json.loads(block("## Tool schemas", "json")) == TOOL_DEFINITIONS
