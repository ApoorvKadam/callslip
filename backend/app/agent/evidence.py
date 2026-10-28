"""Evidence given to the model, and checks on the citations it returns.

Passages go to Claude as `search_result` blocks with citations enabled. Each block's text is
split into groups of a few sentences: a citation quotes whole groups, so smaller groups give
more precise quotes. The API numbers every `search_result` in the conversation in order
(`search_result_index`), so the evidence list is rebuilt from the stored messages in that order.

Every returned citation is checked twice: it must point at evidence we actually sent (index,
source and quoted blocks agree), and the quoted text must appear on the stored page. This proves
provenance (the quote really comes from that page); whether the quote supports the claim is a
separate question, judged in evaluation.
"""

import re
from dataclasses import asdict, dataclass

from app.ingest.chunking import split_sentences

_SOURCE = re.compile(r"^doc-(\d+)/p(\d+)$")
_SPACE = re.compile(r"\s+")
BLOCK_CHARS = 400


def source_for(document_id: int, page_no: int) -> str:
    return f"doc-{document_id}/p{page_no}"


def parse_source(source: str) -> tuple[int, int] | None:
    m = _SOURCE.match(source)
    return (int(m.group(1)), int(m.group(2))) if m else None


def text_blocks(text: str, max_chars: int = BLOCK_CHARS) -> list[str]:
    """Group sentences into blocks of at most about `max_chars` characters."""
    blocks: list[str] = []
    current = ""
    for sentence in split_sentences(text):
        if current and len(current) + 1 + len(sentence) > max_chars:
            blocks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        blocks.append(current)
    return blocks or [text]


def search_result_block(document_id: int, title: str, page_no: int, text: str) -> dict:
    return {
        "type": "search_result",
        "source": source_for(document_id, page_no),
        "title": f"{title}, page {page_no}",
        "content": [{"type": "text", "text": block} for block in text_blocks(text)],
        "citations": {"enabled": True},
    }


@dataclass(frozen=True)
class Evidence:
    source: str
    title: str
    blocks: list[str]


def collect_evidence(messages: list[dict]) -> list[Evidence]:
    """Every search_result in the conversation, in the order the API numbers them."""
    found: list[Evidence] = []

    def take(block: dict) -> None:
        if block.get("type") == "search_result":
            found.append(
                Evidence(block["source"], block["title"], [c["text"] for c in block["content"]])
            )

    for message in messages:
        if message["role"] != "user" or isinstance(message["content"], str):
            continue
        for block in message["content"]:
            take(block)
            if block.get("type") == "tool_result" and isinstance(block.get("content"), list):
                for inner in block["content"]:
                    take(inner)
    return found


def _squash(text: str) -> str:
    """Compare text while ignoring whitespace differences only."""
    return _SPACE.sub("", text)


@dataclass(frozen=True)
class Citation:
    number: int
    source: str
    title: str
    document_id: int | None
    page_no: int | None
    cited_text: str
    provenance: str  # verified | unknown_index | source_mismatch | text_mismatch | not_on_page


def check_citation(
    citation: dict, evidence: list[Evidence], page_texts: dict[tuple[int, int], str]
) -> str:
    index = citation.get("search_result_index")
    if index is None or not 0 <= index < len(evidence):
        return "unknown_index"
    item = evidence[index]
    if item.source != citation.get("source"):
        return "source_mismatch"
    start, end = citation.get("start_block_index", 0), citation.get("end_block_index", 0)
    quoted = _squash(citation.get("cited_text", ""))
    if not quoted or quoted != _squash("".join(item.blocks[start:end])):
        return "text_mismatch"
    location = parse_source(item.source)
    if location is None or quoted not in _squash(page_texts.get(location, "")):
        return "not_on_page"
    return "verified"


def cited_pages(content: list[dict]) -> set[tuple[int, int]]:
    """The (document, page) pairs an answer cites, to load their stored text."""
    pages = set()
    for block in content:
        for c in block.get("citations") or []:
            location = parse_source(c.get("source", ""))
            if location:
                pages.add(location)
    return pages


def build_answer(
    content: list[dict], evidence: list[Evidence], page_texts: dict[tuple[int, int], str]
) -> dict:
    """Turn the model's text blocks into numbered, checked citations for the UI and storage."""
    segments: list[dict] = []
    numbered: dict[tuple[str, str], Citation] = {}
    for block in content:
        if block.get("type") != "text":
            continue
        refs: list[int] = []
        for c in block.get("citations") or []:
            if c.get("type") != "search_result_location":
                continue
            key = (c.get("source", ""), c.get("cited_text", ""))
            if key not in numbered:
                location = parse_source(key[0])
                numbered[key] = Citation(
                    number=len(numbered) + 1,
                    source=key[0],
                    title=c.get("title", ""),
                    document_id=location[0] if location else None,
                    page_no=location[1] if location else None,
                    cited_text=key[1],
                    provenance=check_citation(c, evidence, page_texts),
                )
            if numbered[key].number not in refs:
                refs.append(numbered[key].number)
        segments.append({"text": block["text"], "citations": refs})
    citations = [asdict(c) for c in numbered.values()]
    return {
        "text": "".join(s["text"] for s in segments),
        "segments": segments,
        "citations": citations,
        "citations_verified": sum(c["provenance"] == "verified" for c in citations),
    }
