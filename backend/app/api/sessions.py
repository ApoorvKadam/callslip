"""Sessions and the questions asked in them.

Session isolation without accounts: the first `POST /api/sessions` gives the browser a random
capability token in an HttpOnly, SameSite=Strict cookie. Sessions belong to the token's hash,
and every session and run lookup filters on it, so another browser gets 404 for ids it does
not own. Documents are shared on purpose: this is a single-tenant demo corpus.
"""

import hashlib
import json
import re
import secrets
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from psycopg import errors
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, StringConstraints

from app.api.auth import Viewer, take_attempt
from app.api.deps import get_pool
from app.runs import queue

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
    "compare_id",
)
RUN_FIELDS = ", ".join(RUN_COLUMNS)


def clarify_fields(table: str) -> str:
    """The run's latest clarifying question and the user's reply to that question, shown together
    in the conversation. Until a run worker records the reply as an event, it is in the run's
    queued resume work; a question not answered yet has no reply."""
    latest = (
        f"(SELECT max(c.seq) FROM run_events c WHERE c.run_id = {table}.id"
        " AND c.type = 'clarification')"
    )
    return (
        f"(SELECT e.data->>'question' FROM run_events e WHERE e.run_id = {table}.id"
        f" AND e.type = 'clarification' AND e.seq = {latest}) AS asked, "
        f"coalesce((SELECT e.data->>'reply' FROM run_events e WHERE e.run_id = {table}.id"
        f" AND e.type = 'clarification_answered' AND e.seq > {latest} ORDER BY e.seq LIMIT 1),"
        f" CASE WHEN {table}.work = 'resume' THEN {table}.work_data->'event'->>'reply' END)"
        " AS replied"
    )


def owner_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# What secrets.token_urlsafe(32) produces; any other cookie value is treated as no token.
_TOKEN = re.compile(r"[A-Za-z0-9_-]{43}")


def valid_token(token: str | None) -> bool:
    return bool(token and _TOKEN.fullmatch(token))


def owner_key(token: str | None, user: int | None) -> str:
    """Whose a conversation is. Signed in, it belongs to the account, so its history follows the
    user to any browser; signed out, it belongs to this browser's token. Signing in or out
    therefore switches to the other set of conversations, and one account never sees another's
    answers, which can quote private documents, on a shared browser. An account key hashes a
    JSON pair, which a bare token can never equal."""
    return owner_hash(json.dumps(["account", user]) if user is not None else str(token))


def owner_or_none(request: Request, user: int | None) -> str | None:
    if user is not None:
        return owner_key(None, user)
    token = request.cookies.get(COOKIE)
    return owner_key(token, None) if valid_token(token) else None


def current_owner(request: Request, user: Viewer) -> str:
    owner = owner_or_none(request, user)
    if owner is None:
        # Same answer as an unknown id: nothing to learn from probing.
        raise HTTPException(404, "Not found.")
    return owner


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
async def create_session(request: Request, response: Response, pool: Pool, user: Viewer) -> dict:
    token = request.cookies.get(COOKIE)
    if not valid_token(token):
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            COOKIE,
            token,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="strict",
            path="/api",
            secure=request.app.state.settings.cookie_secure,
        )
    session_id = uuid4()
    async with pool.connection() as conn:
        await conn.execute(
            "INSERT INTO sessions (id, owner_hash) VALUES (%s, %s)",
            (session_id, owner_key(token, user)),
        )
    return {"id": str(session_id)}


@router.get("/sessions")
async def list_sessions(request: Request, pool: Pool, user: Viewer) -> list[dict]:
    """Past conversations, the most recently used first: each one's first question, its number
    of questions and when it was last used. Conversations with no question yet are left out."""
    owner = owner_or_none(request, user)
    if owner is None:
        return []
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            "SELECT s.id, s.created_at, count(r.id) AS questions, max(r.created_at) AS last_at,"
            "       (array_agg(r.question ORDER BY r.created_at))[1] AS title,"
            "       bool_or(r.compare_id IS NOT NULL) AS compare"
            "  FROM sessions s JOIN runs r ON r.session_id = s.id"
            " WHERE s.owner_hash = %s"
            " GROUP BY s.id ORDER BY last_at DESC LIMIT 50",
            (owner,),
        )
        return await cur.fetchall()


@router.get("/sessions/{session_id}")
async def get_session(session_id: UUID, pool: Pool, owner: Owner) -> dict:
    session = await owned_session(pool, session_id, owner)
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            f"SELECT {RUN_FIELDS}, {clarify_fields('runs')} FROM runs"
            " WHERE session_id = %s ORDER BY created_at",
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


async def limit_questions(request: Request) -> None:
    """Refuse a question beyond `ask_limit` per `ask_window_s` from one client address."""
    settings = request.app.state.settings
    if settings.ask_limit <= 0:
        return
    address = request.client.host if request.client else "unknown"
    key = "ask:addr:" + hashlib.sha256(address.encode()).hexdigest()
    wait = await take_attempt(
        request.app.state.redis, key, settings.ask_limit, settings.ask_window_s
    )
    if wait:
        raise HTTPException(
            429,
            f"Too many questions from this address. Try again in {-(-wait // 60)} min.",
            headers={"Retry-After": str(wait)},
        )


@router.post("/sessions/{session_id}/runs", status_code=202)
async def ask(
    session_id: UUID, body: AskRequest, request: Request, pool: Pool, owner: Owner, user: Viewer
):
    await owned_session(pool, session_id, owner)
    state = request.app.state
    if state.llm is None:
        raise HTTPException(503, "Answering is not configured: set ANTHROPIC_API_KEY.")
    if body.faults and not state.settings.allow_fault_injection:
        raise HTTPException(403, "Fault injection is disabled on this server.")
    await limit_questions(request)
    question = body.question
    history = await recent_history(pool, session_id, state.settings.history_turns)
    run_id = uuid4()
    try:
        async with pool.connection() as conn, conn.transaction():
            # The same lock as a comparison takes, so neither can slip in beside the other.
            await conn.execute("SELECT 1 FROM sessions WHERE id = %s FOR UPDATE", (session_id,))
            if await is_comparison(conn, session_id):
                raise HTTPException(
                    409, "A comparison holds one question. Start a new conversation."
                )
            faults = dict(body.faults or {})
            event = {"mode": body.mode, "question": question, "faults": faults}
            row = await queue.enqueue_start(
                conn,
                run_id,
                session_id,
                body.mode,
                question,
                user,
                faults,
                {"event": event, "history": history},
            )
            run = {k: row[k] for k in RUN_COLUMNS} | {"asked": None, "replied": None}
    except errors.UniqueViolation:
        raise HTTPException(
            409, "This session already has a question in progress. Wait for it, or answer it."
        ) from None

    # A run worker claims the run and executes it (app/runner.py).
    return run


async def is_comparison(conn, session_id: UUID) -> bool:
    cur = await conn.execute(
        "SELECT 1 FROM runs WHERE session_id = %s AND compare_id IS NOT NULL LIMIT 1",
        (session_id,),
    )
    return await cur.fetchone() is not None


class CompareRequest(BaseModel):
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]


@router.post("/sessions/{session_id}/compare", status_code=202)
async def compare(
    session_id: UUID, body: CompareRequest, request: Request, pool: Pool, owner: Owner, user: Viewer
) -> list[dict]:
    """Ask one question both ways at once, in a new, empty conversation: the agent and the single
    pass run side by side on the same documents and model, so their answers can be compared."""
    await owned_session(pool, session_id, owner)
    if request.app.state.llm is None:
        raise HTTPException(503, "Answering is not configured: set ANTHROPIC_API_KEY.")
    await limit_questions(request)
    compare_id = uuid4()
    runs = []
    async with pool.connection() as conn, conn.transaction():
        # Locked, so a question asked at the same moment cannot slip in beside the pair.
        await conn.execute("SELECT 1 FROM sessions WHERE id = %s FOR UPDATE", (session_id,))
        cur = await conn.execute("SELECT 1 FROM runs WHERE session_id = %s LIMIT 1", (session_id,))
        if await cur.fetchone() is not None:
            raise HTTPException(409, "Compare in a new conversation.")
        for mode in ("agent", "baseline"):
            event = {"mode": mode, "question": body.question, "faults": {}}
            row = await queue.enqueue_start(
                conn,
                uuid4(),
                session_id,
                mode,
                body.question,
                user,
                {},
                {"event": event, "history": []},
                compare_id,
            )
            runs.append({k: row[k] for k in RUN_COLUMNS} | {"asked": None, "replied": None})
    return runs


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
    session_id: UUID,
    run_id: UUID,
    body: ResumeRequest,
    request: Request,
    pool: Pool,
    owner: Owner,
    user: Viewer,
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
            # The same reply, sent again: the same answer as the first time.
            cur = conn.cursor(row_factory=dict_row)
            await cur.execute(
                f"SELECT {RUN_FIELDS}, {clarify_fields('runs')} FROM runs WHERE id = %s",
                (run_id,),
            )
            return await cur.fetchone()
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
        # Queued for a run worker, which writes the reply's event and resumes the agent.
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(
            "UPDATE runs SET status = 'running', pending_tool_use_id = NULL, resume_key = %s,"
            " work = 'resume', work_data = %s, updated_at = now()"
            f" WHERE id = %s RETURNING {RUN_FIELDS}, {clarify_fields('runs')}",
            (resume_key, Jsonb({"event": {"reply": body.reply}}), run_id),
        )
        return await cur.fetchone()


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
