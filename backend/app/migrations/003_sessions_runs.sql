-- Sessions, question runs, the raw model conversation, UI events and the model-call ledger.

-- A browser holds a random capability token in an HttpOnly cookie; only its hash is stored.
CREATE TABLE sessions (
    id           UUID PRIMARY KEY,
    owner_hash   TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX sessions_owner_idx ON sessions (owner_hash, created_at);

-- One run answers one question (and its clarification, if the agent asks for one).
CREATE TABLE runs (
    id                   UUID PRIMARY KEY,
    session_id           UUID NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    mode                 TEXT NOT NULL CHECK (mode IN ('agent', 'baseline')),
    question             TEXT NOT NULL,
    status               TEXT NOT NULL DEFAULT 'running' CHECK (status IN (
                             'running', 'needs_clarification', 'complete',
                             'incomplete', 'failed', 'abandoned')),
    status_reason        TEXT,
    answer               JSONB,
    pending_tool_use_id  TEXT,
    resume_key           TEXT,
    model_turns          INTEGER NOT NULL DEFAULT 0,
    tool_calls           INTEGER NOT NULL DEFAULT 0,
    exec_ms              INTEGER NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at          TIMESTAMPTZ
);
CREATE INDEX runs_session_idx ON runs (session_id, created_at);
-- At most one unresolved run per session: a new question waits until it ends or is abandoned.
CREATE UNIQUE INDEX runs_one_unresolved_per_session
    ON runs (session_id) WHERE status IN ('running', 'needs_clarification');

-- The exact model conversation, append-only, in order. Needed to resume after a clarification
-- or a restart, and to re-check citations. Never shown to users (it holds thinking blocks).
CREATE TABLE run_messages (
    run_id      UUID NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    seq         INTEGER NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, seq)
);

-- What the UI trace shows: one row per step, streamed to the browser as server-sent events.
CREATE TABLE run_events (
    run_id      UUID NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    seq         INTEGER NOT NULL,
    type        TEXT NOT NULL,
    data        JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, seq)
);

-- Every model call with its token usage and estimated cost.
CREATE TABLE llm_calls (
    id                     BIGSERIAL PRIMARY KEY,
    run_id                 UUID REFERENCES runs (id) ON DELETE SET NULL,
    purpose                TEXT NOT NULL,
    model                  TEXT NOT NULL,
    input_tokens           INTEGER NOT NULL,
    output_tokens          INTEGER NOT NULL,
    cache_creation_tokens  INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens      INTEGER NOT NULL DEFAULT 0,
    cost_usd               NUMERIC(10, 6) NOT NULL,
    ms                     INTEGER NOT NULL,
    stop_reason            TEXT,
    request_id             TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX llm_calls_run_idx ON llm_calls (run_id);
