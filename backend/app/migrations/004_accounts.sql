-- Accounts and personal documents. A signed-in user's uploads are visible only to that user;
-- documents with no owner form the shared collection that everyone sees.

CREATE TABLE users (
    id             BIGSERIAL PRIMARY KEY,
    email          TEXT NOT NULL,
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX users_email_idx ON users (lower(email));

-- The browser holds a random sign-in token in an HttpOnly cookie; only its hash is stored.
CREATE TABLE auth_tokens (
    token_hash  TEXT PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX auth_tokens_user_idx ON auth_tokens (user_id);

ALTER TABLE documents ADD COLUMN owner_user_id BIGINT REFERENCES users (id) ON DELETE CASCADE;
CREATE INDEX documents_owner_idx ON documents (owner_user_id);
-- The same PDF can be in the shared collection once and in each user's own documents once.
-- NULLS NOT DISTINCT keeps the shared collection free of duplicates, as before.
ALTER TABLE documents DROP CONSTRAINT documents_sha256_key;
CREATE UNIQUE INDEX documents_sha256_owner_idx
    ON documents (sha256, owner_user_id) NULLS NOT DISTINCT;

-- Who asked: the agent's tools see the shared collection plus this user's own documents.
ALTER TABLE runs ADD COLUMN user_id BIGINT REFERENCES users (id) ON DELETE SET NULL;
