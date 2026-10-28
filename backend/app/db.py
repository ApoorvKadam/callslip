"""PostgreSQL access: numbered SQL migrations and one async connection pool per process."""

import logging
from importlib import resources

import psycopg
from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool

log = logging.getLogger(__name__)

# Advisory lock id: the API and the worker both migrate at startup, never at the same time.
MIGRATION_LOCK_ID = 7_301


async def migrate(database_url: str) -> None:
    """Apply every `app/migrations/NNN_*.sql` not yet recorded, each in its own transaction."""
    async with await psycopg.AsyncConnection.connect(database_url, autocommit=True) as conn:
        await conn.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_LOCK_ID,))
        try:
            await conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                " name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
            )
            cur = await conn.execute("SELECT name FROM schema_migrations")
            applied = {row[0] for row in await cur.fetchall()}
            files = sorted(
                (f for f in resources.files("app.migrations").iterdir() if f.name.endswith(".sql")),
                key=lambda f: f.name,
            )
            for f in files:
                if f.name in applied:
                    continue
                async with conn.transaction():
                    await conn.execute(f.read_text())
                    await conn.execute(
                        "INSERT INTO schema_migrations (name) VALUES (%s)", (f.name,)
                    )
                log.info("migration applied", extra={"fields": {"migration": f.name}})
        finally:
            await conn.execute("SELECT pg_advisory_unlock(%s)", (MIGRATION_LOCK_ID,))


async def open_pool(database_url: str, max_size: int = 10) -> AsyncConnectionPool:
    """Open a pool whose connections already understand the pgvector `vector` type."""
    pool = AsyncConnectionPool(
        database_url, min_size=1, max_size=max_size, configure=register_vector_async, open=False
    )
    await pool.open(wait=True, timeout=30)
    return pool
