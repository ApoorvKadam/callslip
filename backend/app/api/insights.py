"""How the viewer's own questions went over the last 30 days: outcomes, time, cost and how they
rated the answers.

Only the viewer's conversations are counted (the same owner as every run endpoint): accounts are
not verified, so no one can be trusted with other people's activity here. Numbers only; no
question, answer or note leaves this endpoint. Deployment-wide run and cost totals are in
/metrics, for operators.
"""

from fastapi import APIRouter, Request
from psycopg.rows import dict_row

from app.api.auth import Viewer
from app.api.sessions import Pool, owner_or_none

router = APIRouter(prefix="/api/insights", tags=["insights"])

WINDOW_DAYS = 30

_RUNS = """
    SELECT count(*) AS runs,
           count(*) FILTER (WHERE r.status = 'complete') AS complete,
           count(*) FILTER (WHERE r.status = 'incomplete') AS incomplete,
           count(*) FILTER (WHERE r.status = 'failed') AS failed,
           count(*) FILTER (WHERE r.status IN ('running', 'needs_clarification')) AS open,
           count(*) FILTER (WHERE r.status = 'abandoned') AS abandoned,
           count(*) FILTER (WHERE EXISTS (SELECT 1 FROM run_events e
                                           WHERE e.run_id = r.id AND e.type = 'clarification'))
               AS asked_to_clarify,
           percentile_disc(0.5) WITHIN GROUP (ORDER BY r.exec_ms)
               FILTER (WHERE r.finished_at IS NOT NULL AND r.answer IS NOT NULL) AS median_ms,
           count(*) FILTER (WHERE r.finished_at IS NOT NULL AND r.answer IS NOT NULL) AS rateable,
           count(f.run_id) FILTER (WHERE f.helpful) AS useful,
           count(f.run_id) FILTER (WHERE NOT f.helpful) AS not_useful,
           coalesce(sum(jsonb_array_length(r.answer->'citations')), 0) AS citations,
           coalesce(sum((r.answer->>'citations_verified')::int), 0) AS citations_verified
      FROM runs r
      JOIN sessions s ON s.id = r.session_id
      LEFT JOIN run_feedback f ON f.run_id = r.id
     WHERE s.owner_hash = %(owner)s AND r.created_at > now() - make_interval(days => %(days)s)
"""

# Model calls are summed apart from the join above, so each call counts once.
_COST = """
    SELECT coalesce(sum(c.cost_usd), 0)::float AS cost_usd
      FROM llm_calls c
      JOIN runs r ON r.id = c.run_id
      JOIN sessions s ON s.id = r.session_id
     WHERE s.owner_hash = %(owner)s AND r.created_at > now() - make_interval(days => %(days)s)
"""


@router.get("")
async def insights(request: Request, pool: Pool, user: Viewer) -> dict:
    owner = owner_or_none(request, user)
    params = {"owner": owner or "", "days": WINDOW_DAYS}
    async with pool.connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        await cur.execute(_RUNS, params)
        totals = await cur.fetchone()
        await cur.execute(_COST, params)
        totals |= await cur.fetchone()
    return {"days": WINDOW_DAYS, **totals}
