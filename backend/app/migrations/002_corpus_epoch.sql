-- A random identity for this database's corpus, part of every cache key with the version.
-- Without it, a recreated or restored database restarts its version numbers and Redis could
-- serve results cached for a different corpus that once had the same version.
ALTER TABLE corpus_state ADD COLUMN epoch UUID NOT NULL DEFAULT gen_random_uuid();
