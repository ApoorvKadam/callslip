"""Sessions and the questions asked in them.

Session isolation without accounts: the first `POST /api/sessions` gives the browser a random
capability token in an HttpOnly, SameSite=Strict cookie. Sessions belong to the token's hash,
and every session and run lookup filters on it, so another browser gets 404 for ids it does
not own. Documents are shared on purpose: this is a single-tenant demo corpus.
"""

import hashlib
import json
import secrets
import time
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from psycopg import errors
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, StringConstraints

from app.agent.baseline import run_baseline
from app.agent.loop import resume_agent, start_agent
from app.api.deps import get_pool
from app.runs.context import RunContext

router = APIRouter(prefix="/api", tags=["sessions"])

COOKIE = "rag_client"
COOKIE_MAX_AGE = 30 * 24 * 3600
# What clients see of a run (the raw model conversation and resume keys stay server-side).
RUN_COLUMNS = (
    "id",
    "session_id",
    "mode",
    "question",
    "status",
    "status_reason",
    "answer",
    "model_turns",
    "tool_calls",
    "exec_ms",
    "created_at",
    "finished_at",
)
RUN_FIELDS = ", ".join(RUN_COLUMNS)


def owner_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def current_owner(request: Request) -> str:
    token = request.cookies.get(COOKIE)
    if not token or len(token) < 32:
        # Same answer as an unknown id: nothing to learn from probing.
        raise HTTPException(404, "Not found.")
    return owner_hash(token)


Owner = Annotated[str, Depends(current_owner)]
Pool = Annotated[AsyncConnectionPool, Depends(get_pool)]


async def owned_session(pool: AsyncConnectionPool, session_id: UUID, owner: str) -> dict:
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            "SELECT id, created_at FROM sessions WHERE id = %s AND owner_hash = %s",
            (session_id, owner),
        )
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(404, "Not found.")
    return row


@router.post("/sessions", status_code=201)
async def create_session(request: Request, response: Response, pool: Pool) -> dict:
    token = request.cookies.get(COOKIE)
    if not token or len(token) < 32:
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            COOKIE, token, max_age=COOKIE_MAX_AGE, httponly=True, samesite="strict", path="/api"
        )
    session_id = uuid4()
    async with pool.connection() as conn:
        await conn.execute(
            "INSERT INTO sessions (id, owner_hash) VALUES (%s, %s)", (session_id, owner_hash(token))
        )
    return {"id": str(session_id)}


@router.get("/sessions/{session_id}")
async def get_session(session_id: UUID, pool: Pool, owner: Owner) -> dict:
    session = await owned_session(pool, session_id, owner)
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            f"SELECT {RUN_FIELDS} FROM runs WHERE session_id = %s ORDER BY created_at",
            (session_id,),
        )
        runs = await cur.fetchall()
    return {"id": str(session["id"]), "created_at": session["created_at"], "runs": runs}


class AskRequest(BaseModel):
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]
    mode: Literal["agent", "baseline"] = "agent"
    # Evaluation only: make a tool fail on purpose. Refused unless ALLOW_FAULT_INJECTION=true.
    faults: (
        dict[
            Literal["search_documents", "read_document_section", "list_documents"],
            Literal["timeout", "timeout_once", "error", "error_once"],
        ]
        | None
    ) = None


async def recent_history(pool: AsyncConnectionPool, session_id: UUID, limit: int):
    """Earlier finished questions and answers of this session, oldest first, as plain text."""
    async with pool.connection() as conn:
        cur = await conn.execute(
            "SELECT question, answer->>'text' FROM runs WHERE session_id = %s"
            " AND status IN ('complete', 'incomplete') AND answer IS NOT NULL"
            " ORDER BY created_at DESC LIMIT %s",
            (session_id, limit),
        )
        rows = await cur.fetchall()
    return [(q, a[:1500]) for q, a in reversed(rows)]


@router.post("/sessions/{session_id}/runs", status_code=202)
async def ask(session_id: UUID, body: AskRequest, request: Request, pool: Pool, owner: Owner):
    await owned_session(pool, session_id, owner)
    state = request.app.state
    if state.llm is None:
        raise HTTPException(503, "Answering is not configured: set ANTHROPIC_API_KEY.")
    if body.faults and not state.settings.allow_fault_injection:
        raise HTTPException(403, "Fault injection is disabled on this server.")
    question = body.question
    history = await recent_history(pool, session_id, state.settings.history_turns)
    run_id = uuid4()
    try:
        async with pool.connection() as conn:
            cur = conn.cursor(row_factory=dict_row)
            await cur.execute(
                "INSERT INTO runs (id, session_id, mode, question) VALUES (%s, %s, %s, %s)"
                f" RETURNING {RUN_FIELDS}",
                (run_id, session_id, body.mode, question),
            )
            run = await cur.fetchone()
    except errors.UniqueViolation:
        raise HTTPException(
            409, "This session already has a question in progress. Wait for it, or answer it."
        ) from None

    ctx = RunContext(run_id, session_id, state.store, state.llm, state.search, state.settings)
    await ctx.emit(
        "run_started", {"mode": body.mode, "question": question, "faults": body.faults or {}}
    )
    if body.mode == "agent":
        work = start_agent(ctx, question, history, dict(body.faults or {}))
    else:
        work = run_baseline(ctx, question, history, dict(body.faults or {}))
    state.runs.start(run_id, work)
    return run


class ResumeRequest(BaseModel):
    tool_use_id: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    idempotency_key: Annotated[str, StringConstraints(min_length=8, max_length=100)]
    reply: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


async def owned_run_for_update(conn, session_id: UUID, run_id: UUID, owner: str) -> dict:
    cur = conn.cursor(row_factory=dict_row)
    await cur.execute(
        "SELECT r.* FROM runs r JOIN sessions s ON s.id = r.session_id"
        " WHERE r.id = %s AND r.session_id = %s AND s.owner_hash = %s FOR UPDATE OF r",
        (run_id, session_id, owner),
    )
    run = await cur.fetchone()
    if run is None:
        raise HTTPException(404, "Not found.")
    return run


@router.post("/sessions/{session_id}/runs/{run_id}/resume", status_code=202)
async def resume(
    session_id: UUID, run_id: UUID, body: ResumeRequest, request: Request, pool: Pool, owner: Owner
):
    """Answer the agent's clarifying question. Exactly once: a retry with the same key and reply
    gets the recorded outcome; the same key with another reply, or a stale reply, gets 409."""
    state = request.app.state
    if state.llm is None:
        raise HTTPException(503, "Answering is not configured: set ANTHROPIC_API_KEY.")
    async with pool.connection() as conn, conn.transaction():
        run = await owned_run_for_update(conn, session_id, run_id, owner)
        payload = json.dumps([body.tool_use_id, body.reply])  # unambiguous, unlike joining
        reply_hash = hashlib.sha256(payload.encode()).hexdigest()
        resume_key = f"{body.idempotency_key}:{reply_hash[:16]}"
        if run["resume_key"] == resume_key:
            return {k: run[k] for k in RUN_COLUMNS}  # the same reply, sent again
        if (run["resume_key"] or "").rpartition(":")[0] == body.idempotency_key:
            raise HTTPException(409, "This key was already used for a different reply.")
        if run["status"] != "needs_clarification" or run["pending_tool_use_id"] != body.tool_use_id:
            raise HTTPException(409, "This question is not waiting for that reply.")
        result = {
            "type": "tool_result",
            "tool_use_id": body.tool_use_id,
            "content": f"The user replied: {body.reply}",
        }
        await conn.execute(
            "INSERT INTO run_messages (run_id, seq, role, content)"
            " SELECT %s, coalesce(max(seq), 0) + 1, 'user', %s FROM run_messages WHERE run_id = %s",
            (run_id, Jsonb([result]), run_id),
        )
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            "UPDATE runs SET status = 'running', pending_tool_use_id = NULL, resume_key = %s,"
            f" updated_at = now() WHERE id = %s RETURNING {RUN_FIELDS}",
            (resume_key, run_id),
        )
        updated = await cur.fetchone()

    ctx = RunContext(run_id, session_id, state.store, state.llm, state.search, state.settings)
    # Waiting for the user does not count against the run's time budget.
    ctx.started = time.monotonic() - run["exec_ms"] / 1000
    ctx.model_turns, ctx.tool_calls = run["model_turns"], run["tool_calls"]
    await ctx.emit("clarification_answered", {"reply": body.reply})
    state.runs.start(run_id, resume_agent(ctx))
    return updated


@router.post("/sessions/{session_id}/runs/{run_id}/abandon")
async def abandon(session_id: UUID, run_id: UUID, request: Request, pool: Pool, owner: Owner):
    """Skip a pending clarification, so the session can take a new question."""
    async with pool.connection() as conn, conn.transaction():
        run = await owned_run_for_update(conn, session_id, run_id, owner)
        if run["status"] != "needs_clarification":
            raise HTTPException(409, "Only a question waiting for a reply can be skipped.")
        await conn.execute(
            "UPDATE runs SET status = 'abandoned', status_reason = 'skipped by the user',"
            " pending_tool_use_id = NULL, updated_at = now(), finished_at = now() WHERE id = %s",
            (run_id,),
        )
    await request.app.state.store.event(
        run_id, "run_finished", {"status": "abandoned", "reason": "skipped by the user"}
    )
    return {"id": str(run_id), "status": "abandoned"}
