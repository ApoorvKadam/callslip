-- Documents, their raw bytes, extracted pages and searchable chunks.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id           BIGSERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    filename     TEXT NOT NULL,
    sha256       TEXT NOT NULL UNIQUE,
    byte_size    INTEGER NOT NULL,
    page_count   INTEGER,
    status       TEXT NOT NULL DEFAULT 'queued'
                 CHECK (status IN ('queued', 'processing', 'ready', 'failed')),
    error        TEXT,
    -- Ingestion job state: Postgres owns the job, a worker holds a time-limited lease.
    attempts     INTEGER NOT NULL DEFAULT 0,
    lease_owner  TEXT,
    lease_until  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX documents_status_idx ON documents (status, created_at);

-- Raw PDF bytes live in Postgres: one volume to back up for a corpus this size.
CREATE TABLE document_files (
    document_id  BIGINT PRIMARY KEY REFERENCES documents (id) ON DELETE CASCADE,
    content      BYTEA NOT NULL
);

-- Physical PDF pages (1-based), text exactly as extracted.
CREATE TABLE pages (
    document_id  BIGINT NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    page_no      INTEGER NOT NULL,
    text         TEXT NOT NULL,
    PRIMARY KEY (document_id, page_no)
);

-- Chunks never cross a page, so every citation maps to exactly one page.
-- `text` is the evidence shown to the model; `search_text` adds a title header for retrieval.
CREATE TABLE chunks (
    id           BIGSERIAL PRIMARY KEY,
    document_id  BIGINT NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    page_no      INTEGER NOT NULL,
    chunk_index  INTEGER NOT NULL,
    text         TEXT NOT NULL,
    search_text  TEXT NOT NULL,
    token_count  INTEGER NOT NULL,
    embedding    vector(384) NOT NULL,
    tsv          tsvector GENERATED ALWAYS AS (to_tsvector('english', search_text)) STORED,
    UNIQUE (document_id, page_no, chunk_index)
);
CREATE INDEX chunks_tsv_idx ON chunks USING GIN (tsv);
CREATE INDEX chunks_document_page_idx ON chunks (document_id, page_no);

-- Bumped in the same transaction that publishes a document; part of every cache key.
CREATE TABLE corpus_state (
    id       INTEGER PRIMARY KEY CHECK (id = 1),
    version  BIGINT NOT NULL
);
INSERT INTO corpus_state (id, version) VALUES (1, 0);
