#!/usr/bin/env bash
# Verify a running stack: container health, API liveness and readiness, then an end-to-end
# upload, ingestion and search (scripts/smoke_test.py). Exits non-zero on any failure.
set -euo pipefail
cd "$(dirname "$0")/.."
port="$(docker compose port frontend 8080 2>/dev/null | sed 's/.*://' || true)"
base="${BASE_URL:-http://localhost:${port:-8080}}"

docker compose ps --format 'table {{.Service}}\t{{.Status}}'
# Every service in the Compose file must have a container.
expected="$(docker compose config --services | LC_ALL=C sort -u)"
present="$(docker compose ps --all --format '{{.Service}}' | LC_ALL=C sort -u)"
missing="$(comm -23 <(echo "$expected") <(echo "$present"))"
if [[ -n "$missing" ]]; then
  echo "missing: $(echo $missing)" >&2
  exit 1
fi
# Every service must be running, and healthy when it has a health check.
unhealthy="$(docker compose ps --all --format '{{.Service}} {{.State}} {{.Health}}' |
  awk '$2 != "running" || ($3 != "" && $3 != "healthy") {print $1}')"
if [[ -n "$unhealthy" ]]; then
  echo "not healthy: $(echo $unhealthy)" >&2
  exit 1
fi
python3 scripts/smoke_test.py --base "$base"
echo "verify: ok"
