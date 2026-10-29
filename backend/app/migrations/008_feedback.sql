-- A user's verdict on one finished answer: useful or not, and on "not useful" an optional note
-- saying what was missing. Rating the answer again replaces the earlier verdict.
CREATE TABLE run_feedback (
    run_id      UUID PRIMARY KEY REFERENCES runs (id) ON DELETE CASCADE,
    helpful     BOOLEAN NOT NULL,
    note        TEXT CHECK (char_length(note) <= 500),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
