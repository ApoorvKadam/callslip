"""FastAPI application: `uvicorn app.main:app`."""

import asyncio
from contextlib import asynccontextmanager

from anthropic import AsyncAnthropic
from fastapi import FastAPI
from redis.asyncio import Redis

from app.api import auth, documents, health, runs, search, sessions
from app.cache import Cache
from app.config import get_settings
from app.db import migrate, open_pool
from app.embeddings import Embedder
from app.llm import LLM
from app.logs import setup_logging
from app.retrieval.search import SearchService
from app.runs.manager import RunManager, close_interrupted_runs
from app.runs.store import RunStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    await migrate(settings.database_url)
    app.state.pool = await open_pool(settings.database_url)
    # Short timeouts: Redis is a cache, so a slow or missing Redis must never stall a request.
    app.state.redis = Redis.from_url(
        settings.redis_url, socket_timeout=0.25, socket_connect_timeout=0.25
    )
    # The API embeds queries with the same local model the worker used for the passages.
    embedder = await asyncio.to_thread(
        Embedder,
        settings.embed_model,
        settings.fastembed_cache_path,
        settings.embed_threads,
        settings.embed_batch_size,
    )
    app.state.search = SearchService(app.state.pool, embedder, Cache(app.state.redis))
    app.state.settings = settings
    app.state.store = RunStore(app.state.pool)
    app.state.runs = RunManager(app.state.store)
    # Without a key the app still serves documents and search; asking returns 503.
    app.state.llm = (
        LLM(
            AsyncAnthropic(api_key=settings.anthropic_api_key, max_retries=2),
            app.state.pool,
            settings.answer_model,
            settings.answer_effort,
        )
        if settings.anthropic_api_key
        else None
    )
    await close_interrupted_runs(app.state.pool)
    try:
        yield
    finally:
        await app.state.runs.shutdown()
        await app.state.redis.aclose()
        await app.state.pool.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Callslip", version="0.1.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(search.router)
    app.include_router(sessions.router)
    app.include_router(runs.router)
    return app


app = create_app()
