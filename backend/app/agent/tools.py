"""The agent's tools: four read-only corpus tools and one control tool.

Contract for every read tool, documented to the model and tested:
- success: `search_result` blocks (search, read section) or a JSON object (list documents,
  outline);
- empty: JSON text `{"status": "no_results", ...}`, which is not an error;
- invalid arguments: `is_error` result with JSON `{"status": "invalid_input", "error": ...}`
  explaining how to fix the call (never retried: the model has to change the call);
- failure or timeout: `is_error` result with JSON `{"status": "error" | "timeout", ...}`.
A tool_result never mixes `search_result` blocks with text blocks (the API does not allow it).

Tools read only the indexed corpus, through parameterized SQL. None of them can write, call the
network or reach the file system, so instructions hidden in a document have nothing to act on.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, ValidationError, model_validator

from app.agent.evidence import search_result_block
from app.retrieval.search import SearchFilters, SearchService
from app.runs.context import evidence_summary
from app.runs.store import RunStore

MAX_SECTION_PAGES = 3

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "list_documents",
        "description": (
            "List every document in the collection with its id, title and page count. Use it to "
            "learn what exists, to work out which document the user means, or to get ids for "
            "filtering a search."
        ),
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "search_documents",
        "description": (
            "Search the documents by meaning and keywords. Returns up to top_k passages, each "
            "with its document and page. Use focused queries: for a multi-part question, search "
            "each part separately. If the passages do not answer the question, rewrite the "
            "query (other terms, the document's own vocabulary, a document filter) and search "
            'again. Returns {"status": "no_results"} when nothing matches.'
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look for (1-500 chars)."},
                "document_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Only search these documents (ids from the document list).",
                },
                "page_from": {"type": "integer", "description": "First page to include."},
                "page_to": {"type": "integer", "description": "Last page to include."},
                "top_k": {"type": "integer", "description": "Passages to return, 1-10. Default 8."},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_document_section",
        "description": (
            f"Read the full text of up to {MAX_SECTION_PAGES} consecutive pages of one document. "
            "Use it when a passage is cut off, when a list or table continues on the next page, "
            "or to check the context around a passage."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "integer"},
                "page_start": {"type": "integer", "description": "First page, 1-based."},
                "page_end": {"type": "integer", "description": "Last page, inclusive."},
            },
            "required": ["document_id", "page_start", "page_end"],
            "additionalProperties": False,
        },
    },
    {
        "name": "document_outline",
        "description": (
            "List the sections of one document from its own bookmarks, each with the page it "
            "starts on (the page numbers read_document_section uses). Use it to find where a "
            "document covers a topic, for example when search fails or finds only a summary. "
            'Returns {"status": "no_outline"} when the PDF has no bookmarks.'
        ),
        "input_schema": {
            "type": "object",
            "properties": {"document_id": {"type": "integer"}},
            "required": ["document_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "ask_clarification",
        "description": (
            "Ask the user one targeted question when the request has several plausible readings "
            "and guessing could give a wrong answer (for example, which of several memos they "
            "mean). Offer the likely options. Your turn ends until the user replies."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "One short question, at most 500 characters.",
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Up to 6 short choices the user can pick from.",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
]


class SearchArgs(BaseModel, extra="forbid"):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    document_ids: Annotated[list[int] | None, Field(max_length=50)] = None
    page_from: Annotated[int | None, Field(ge=1)] = None
    page_to: Annotated[int | None, Field(ge=1)] = None
    top_k: Annotated[int, Field(ge=1, le=10)] = 8

    @model_validator(mode="after")
    def pages_in_order(self) -> "SearchArgs":
        if self.page_from and self.page_to and self.page_from > self.page_to:
            raise ValueError("page_from must not be after page_to")
        return self


class SectionArgs(BaseModel, extra="forbid"):
    document_id: int
    page_start: Annotated[int, Field(ge=1)]
    page_end: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def valid_range(self) -> "SectionArgs":
        if self.page_end < self.page_start:
            raise ValueError("page_end must not be before page_start")
        if self.page_end - self.page_start + 1 > MAX_SECTION_PAGES:
            raise ValueError(f"read at most {MAX_SECTION_PAGES} pages at a time")
        return self


class ClarificationArgs(BaseModel, extra="forbid"):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    options: Annotated[list[str] | None, Field(max_length=6)] = None


class ListArgs(BaseModel, extra="forbid"):
    pass


class OutlineArgs(BaseModel, extra="forbid"):
    document_id: int


@dataclass
class ToolOutcome:
    content: list[dict] | str
    is_error: bool
    status: str  # ok | no_results | invalid_input | error | timeout | not_run
    summary: str
    trace: dict = field(default_factory=dict)


def _json(payload: dict) -> str:
    return json.dumps(payload, separators=(",", ":"))


def invalid_input(tool: str, exc: ValidationError | ValueError) -> ToolOutcome:
    if isinstance(exc, ValidationError):
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e['loc']) or 'input'}: {e['msg']}" for e in exc.errors()
        )
    else:
        detail = str(exc)
    return ToolOutcome(
        _json({"status": "invalid_input", "tool": tool, "error": detail}),
        True,
        "invalid_input",
        f"invalid input: {detail}",
    )


class Tools:
    """Runs the read tools against the corpus. One instance per run."""

    def __init__(self, search: SearchService, store: RunStore, viewer: int | None = None) -> None:
        self.search = search
        self.store = store
        self.viewer = viewer  # the user who asked: shared documents plus their own

    async def list_documents(self, args: ListArgs) -> ToolOutcome:
        async with self.store.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT id, title, page_count FROM documents WHERE status = 'ready'"
                " AND (owner_user_id IS NULL OR owner_user_id = %s) ORDER BY id",
                (self.viewer,),
            )
            rows = await cur.fetchall()
        if not rows:
            return ToolOutcome(
                _json({"status": "no_results", "message": "No documents are ready yet."}),
                False,
                "no_results",
                "no documents",
            )
        documents = [{"document_id": i, "title": t, "page_count": p} for i, t, p in rows]
        return ToolOutcome(_json({"documents": documents}), False, "ok", f"{len(rows)} documents")

    async def search_documents(self, args: SearchArgs) -> ToolOutcome:
        filters = SearchFilters(
            tuple(args.document_ids) if args.document_ids else None,
            args.page_from,
            args.page_to,
            viewer=self.viewer,
        )
        result = await self.search.search(args.query, filters, args.top_k)
        trace = {"cache": result.cache, "evidence": evidence_summary(result.hits)}
        if not result.hits:
            payload = {
                "status": "no_results",
                "query": args.query,
                "filters": {k: v for k, v in filters.__dict__.items() if v and k != "viewer"},
                "hint": "Rewrite the query with other terms, or remove filters.",
            }
            return ToolOutcome(_json(payload), False, "no_results", "no passages", trace)
        blocks = [
            search_result_block(h.document_id, h.title, h.page_no, h.text) for h in result.hits
        ]
        return ToolOutcome(blocks, False, "ok", f"{len(blocks)} passages", trace)

    async def read_document_section(self, args: SectionArgs) -> ToolOutcome:
        async with self.store.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT title, page_count, status FROM documents WHERE id = %s"
                " AND (owner_user_id IS NULL OR owner_user_id = %s)",
                (args.document_id, self.viewer),
            )
            doc = await cur.fetchone()
            if doc is None or doc[2] != "ready":
                return invalid_input(
                    "read_document_section",
                    ValueError(
                        f"no ready document with id {args.document_id}; "
                        "call list_documents for valid ids"
                    ),
                )
            title, page_count, _ = doc
            if args.page_end > page_count:
                return invalid_input(
                    "read_document_section",
                    ValueError(f"document {args.document_id} has {page_count} pages"),
                )
            cur = await conn.execute(
                "SELECT page_no, text FROM pages WHERE document_id = %s"
                " AND page_no BETWEEN %s AND %s ORDER BY page_no",
                (args.document_id, args.page_start, args.page_end),
            )
            pages = [(p, t) for p, t in await cur.fetchall() if t]
        if not pages:
            return ToolOutcome(
                _json({"status": "no_results", "message": "These pages have no text."}),
                False,
                "no_results",
                "no text on these pages",
            )
        blocks = [search_result_block(args.document_id, title, p, t) for p, t in pages]
        evidence = [
            {"document_id": args.document_id, "title": title, "page_no": p, "excerpt": t[:180]}
            for p, t in pages
        ]
        summary = f"pages {args.page_start}-{args.page_end} of {title}"
        return ToolOutcome(blocks, False, "ok", summary, {"evidence": evidence})

    async def document_outline(self, args: OutlineArgs) -> ToolOutcome:
        async with self.store.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT title, status, outline FROM documents WHERE id = %s"
                " AND (owner_user_id IS NULL OR owner_user_id = %s)",
                (args.document_id, self.viewer),
            )
            doc = await cur.fetchone()
        if doc is None or doc[1] != "ready":
            return invalid_input(
                "document_outline",
                ValueError(
                    f"no ready document with id {args.document_id}; "
                    "call list_documents for valid ids"
                ),
            )
        title, _, outline = doc
        if not outline:
            payload = {
                "status": "no_outline",
                "document_id": args.document_id,
                "message": "This PDF has no bookmarks. Its first pages may hold a table of "
                "contents; its printed page numbers can differ from the PDF's.",
            }
            summary = f"no outline for {title}"
            return ToolOutcome(_json(payload), False, "no_results", summary, {"document": title})
        payload = {"document_id": args.document_id, "title": title, "sections": outline}
        summary = f"{len(outline)} sections of {title}"
        return ToolOutcome(_json(payload), False, "ok", summary, {"document": title})


ARG_MODELS = {
    "list_documents": ListArgs,
    "search_documents": SearchArgs,
    "read_document_section": SectionArgs,
    "document_outline": OutlineArgs,
}


def elapsed_ms(started: float) -> int:
    return int((time.monotonic() - started) * 1000)
