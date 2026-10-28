"""Database access for sessions and runs: messages, events, status changes."""

from typing import Any
from uuid import UUID

from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

TERMINAL = ("complete", "incomplete", "failed", "abandoned")
# Columns a run update may set; anything else is a programming error.
UPDATABLE = {
    "status",
    "status_reason",
    "answer",
    "pending_tool_use_id",
    "resume_key",
    "model_turns",
    "tool_calls",
    "exec_ms",
}


class RunStore:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool = pool

    async def append_message(self, run_id: UUID, role: str, content: list[dict]) -> None:
        async with self.pool.connection() as conn:
            await conn.execute(
                "INSERT INTO run_messages (run_id, seq, role, content)"
                " SELECT %s, coalesce(max(seq), 0) + 1, %s, %s FROM run_messages WHERE run_id = %s",
                (run_id, role, Jsonb(content), run_id),
            )

    async def messages(self, run_id: UUID) -> list[dict]:
        async with self.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT role, content FROM run_messages WHERE run_id = %s ORDER BY seq", (run_id,)
            )
            return [{"role": role, "content": content} for role, content in await cur.fetchall()]

    async def event(self, run_id: UUID, type_: str, data: dict[str, Any]) -> int:
        async with self.pool.connection() as conn:
            cur = await conn.execute(
                "INSERT INTO run_events (run_id, seq, type, data)"
                " SELECT %s, coalesce(max(seq), 0) + 1, %s, %s FROM run_events WHERE run_id = %s"
                " RETURNING seq",
                (run_id, type_, Jsonb(data), run_id),
            )
            return (await cur.fetchone())[0]

    async def update(self, run_id: UUID, **fields: Any) -> None:
        """Set run columns; `finished_at` is stamped when the status becomes terminal."""
        unknown = set(fields) - UPDATABLE
        if unknown:
            raise ValueError(f"cannot update run columns {sorted(unknown)}")
        assignments = [
            sql.SQL("{} = {}").format(sql.Identifier(name), sql.Placeholder(name))
            for name in fields
        ]
        assignments.append(sql.SQL("updated_at = now()"))
        if fields.get("status") in TERMINAL:
            assignments.append(sql.SQL("finished_at = now()"))
        query = sql.SQL("UPDATE runs SET {} WHERE id = {}").format(
            sql.SQL(", ").join(assignments), sql.Placeholder("id")
        )
        params = {
            name: Jsonb(value) if name == "answer" and value is not None else value
            for name, value in fields.items()
        }
        params["id"] = run_id
        async with self.pool.connection() as conn:
            await conn.execute(query, params)

    async def page_texts(self, pages: set[tuple[int, int]]) -> dict[tuple[int, int], str]:
        if not pages:
            return {}
        async with self.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT document_id, page_no, text FROM pages"
                " WHERE (document_id, page_no) IN (SELECT * FROM unnest(%s::bigint[], %s::int[]))",
                ([d for d, _ in pages], [p for _, p in pages]),
            )
            return {(d, p): text for d, p, text in await cur.fetchall()}

    async def get_run(self, run_id: UUID) -> dict | None:
        async with self.pool.connection() as conn:
            cur = conn.cursor(row_factory=dict_row)
            await cur.execute("SELECT * FROM runs WHERE id = %s", (run_id,))
            return await cur.fetchone()

    async def usage_totals(self, run_id: UUID) -> dict:
        async with self.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT count(*), coalesce(sum(input_tokens), 0), coalesce(sum(output_tokens), 0),"
                " coalesce(sum(cache_read_tokens), 0), coalesce(sum(cache_creation_tokens), 0),"
                " coalesce(sum(cost_usd), 0)::float8 FROM llm_calls WHERE run_id = %s",
                (run_id,),
            )
            calls, tin, tout, cread, cwrite, cost = await cur.fetchone()
        return {
            "model_calls": calls,
            "input_tokens": tin,
            "output_tokens": tout,
            "cache_read_tokens": cread,
            "cache_creation_tokens": cwrite,
            "cost_usd": round(cost, 6),
        }
