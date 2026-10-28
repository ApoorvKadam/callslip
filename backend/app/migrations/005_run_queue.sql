-- Runs execute in run workers, not in the API process. The API records the work a run needs
-- (start, or resume after a clarification) and returns; a run worker claims it with a lease that
-- it renews while the run executes. A lease that runs out, because its worker crashed or was
-- stopped, closes the run as interrupted. The API keeps no run state, so it can run as replicas.
ALTER TABLE runs ADD COLUMN work TEXT CHECK (work IN ('start', 'resume'));
-- What the claiming worker needs: the run's first event, and for a start the earlier turns.
ALTER TABLE runs ADD COLUMN work_data JSONB;
-- Kept on the run, so a run resumed after a clarification keeps its injected faults.
ALTER TABLE runs ADD COLUMN faults JSONB NOT NULL DEFAULT '{}';
ALTER TABLE runs ADD COLUMN lease_owner TEXT;
ALTER TABLE runs ADD COLUMN lease_until TIMESTAMPTZ;
CREATE INDEX runs_work_idx ON runs (created_at) WHERE work IS NOT NULL;
CREATE INDEX runs_lease_idx ON runs (lease_until) WHERE status = 'running' AND work IS NULL;
