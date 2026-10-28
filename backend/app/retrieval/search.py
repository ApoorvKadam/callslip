"""Hybrid retrieval: pgvector cosine similarity plus PostgreSQL full-text, fused by rank.

Both searches run over the same filtered candidate set (ready documents only, optional document
ids and page range). Each returns its own top `pool` passages; reciprocal rank fusion (RRF,
k=60) combines them, so a passage found by both ranks highest. Notes:
- Vector search is exact (no ANN index): at a few thousand passages a scan takes milliseconds
  and filters can never under-fill the result, which an approximate index can do.
- Keyword ranking is PostgreSQL's `ts_rank_cd` (cover density), not BM25.
- RRF scores order results; they are not calibrated relevance probabilities.
"""

import asyncio
import hashlib
import json
import time
from dataclasses import asdict, dataclass

import numpy as np
from psycopg_pool import AsyncConnectionPool

from app.cache import Cache
from app.embeddings import Embedder

RRF_K = 60
CANDIDATE_POOL = 30
SEARCH_CACHE_TTL_S = 600
QUERY_EMBEDDING_TTL_S = 86_400

_HYBRID_SQL = """
WITH candidates AS (
    SELECT c.id, c.embedding, c.tsv
      FROM chunks c
      JOIN documents d ON d.id = c.document_id
     WHERE d.status = 'ready'
       AND (d.owner_user_id IS NULL OR d.owner_user_id = %(viewer)s::bigint)
       AND (%(doc_ids)s::bigint[] IS NULL OR c.document_id = ANY(%(doc_ids)s::bigint[]))
       AND (%(page_from)s::int IS NULL OR c.page_no >= %(page_from)s::int)
       AND (%(page_to)s::int IS NULL OR c.page_no <= %(page_to)s::int)
),
vector AS (
    SELECT id, row_number() OVER (ORDER BY embedding <=> %(qvec)s, id) AS rank
      FROM candidates
     ORDER BY embedding <=> %(qvec)s, id
     LIMIT %(pool)s
),
keyword AS (
    SELECT id, row_number() OVER (ORDER BY ts_rank_cd(tsv, q) DESC, id) AS rank
      FROM candidates, websearch_to_tsquery('english', %(qtext)s) AS q
     WHERE tsv @@ q
     ORDER BY ts_rank_cd(tsv, q) DESC, id
     LIMIT %(pool)s
),
fused AS (
    SELECT coalesce(v.id, k.id) AS id, v.rank AS vector_rank, k.rank AS keyword_rank,
           coalesce(1.0 / (%(k)s + v.rank), 0) + coalesce(1.0 / (%(k)s + k.rank), 0) AS score
      FROM vector v
      FULL OUTER JOIN keyword k ON k.id = v.id
)
SELECT f.id, c.document_id, d.title, c.page_no, c.chunk_index, c.text,
       f.score::float8, f.vector_rank, f.keyword_rank
  FROM fused f
  JOIN chunks c ON c.id = f.id
  JOIN documents d ON d.id = c.document_id
 ORDER BY f.score DESC, f.id
 LIMIT %(top_k)s
"""


@dataclass(frozen=True)
class SearchFilters:
    document_ids: tuple[int, ...] | None = None
    page_from: int | None = None
    page_to: int | None = None
    # Who is searching: the shared collection plus this user's own documents. It is part of the
    # cache key, so one user's results are never served to another.
    viewer: int | None = None


@dataclass(frozen=True)
class SearchHit:
    chunk_id: int
    document_id: int
    title: str
    page_no: int
    chunk_index: int
    text: str
    score: float
    vector_rank: int | None
    keyword_rank: int | None


@dataclass(frozen=True)
class SearchResult:
    hits: list[SearchHit]
    cache: str  # hit | miss | unavailable
    ms: int


async def hybrid_search(
    pool: AsyncConnectionPool,
    query: str,
    query_vector: np.ndarray,
    filters: SearchFilters,
    top_k: int,
) -> list[SearchHit]:
    params = {
        "doc_ids": list(filters.document_ids) if filters.document_ids else None,
        "page_from": filters.page_from,
        "page_to": filters.page_to,
        "viewer": filters.viewer,
        "qvec": query_vector,
        "qtext": query,
        "pool": max(CANDIDATE_POOL, top_k),
        "k": RRF_K,
        "top_k": top_k,
    }
    async with pool.connection() as conn:
        cur = await conn.execute(_HYBRID_SQL, params)
        return [SearchHit(*row) for row in await cur.fetchall()]


class SearchService:
    """Hybrid search behind a Redis cache whose keys include the corpus version."""

    def __init__(self, pool: AsyncConnectionPool, embedder: Embedder, cache: Cache) -> None:
        self._pool = pool
        self._embedder = embedder
        self._cache = cache

    async def corpus_key(self) -> str:
        """Identity of the current corpus: database epoch plus version, bumped on publish."""
        async with self._pool.connection() as conn:
            cur = await conn.execute("SELECT epoch, version FROM corpus_state WHERE id = 1")
            epoch, version = await cur.fetchone()
        return f"{epoch}:{version}"

    async def query_vector(self, query: str) -> np.ndarray:
        key = f"qemb:v1:{self._embedder.model_name}:{_digest(query)}"
        cached, _ = await self._cache.get_json(key)
        if cached is not None:
            return np.asarray(cached, dtype=np.float32)
        vector = await asyncio.to_thread(self._embedder.embed_query, query)
        await self._cache.set_json(key, vector.tolist(), QUERY_EMBEDDING_TTL_S)
        return vector

    async def search(self, query: str, filters: SearchFilters, top_k: int) -> SearchResult:
        started = time.monotonic()
        corpus = await self.corpus_key()
        key = (
            f"search:v1:{corpus}:{self._embedder.model_name}:"
            f"{_digest(json.dumps([query, asdict(filters), top_k], sort_keys=True))}"
        )
        cached, status = await self._cache.get_json(key)
        if cached is not None:
            hits = [SearchHit(**h) for h in cached]
        else:
            vector = await self.query_vector(query)
            hits = await hybrid_search(self._pool, query, vector, filters, top_k)
            await self._cache.set_json(key, [asdict(h) for h in hits], SEARCH_CACHE_TTL_S)
        return SearchResult(hits, status, int((time.monotonic() - started) * 1000))


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]
