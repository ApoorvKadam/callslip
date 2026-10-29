-- A comparison asks one question both ways at once: an agent run and a single-pass run in one
-- conversation, sharing a compare_id. Such a conversation holds that one question only.
ALTER TABLE runs ADD COLUMN compare_id UUID;
-- Still at most one unresolved run per conversation, except the two halves of a comparison.
DROP INDEX runs_one_unresolved_per_session;
CREATE UNIQUE INDEX runs_one_unresolved_per_session
    ON runs (session_id) WHERE status IN ('running', 'needs_clarification') AND compare_id IS NULL;
CREATE UNIQUE INDEX runs_one_unresolved_per_comparison_mode
    ON runs (session_id, mode)
    WHERE status IN ('running', 'needs_clarification') AND compare_id IS NOT NULL;
