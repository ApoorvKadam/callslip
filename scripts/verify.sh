#!/usr/bin/env bash
# Verify a running stack: container health, API liveness and readiness, then an end-to-end
# upload, ingestion and search (scripts/smoke_test.py). Exits non-zero on any failure.
set -euo pipefail
cd "$(dirname "$0")/.."
port="$(docker compose port frontend 8080 2>/dev/null | sed 's/.*://')"
base="${BASE_URL:-http://localhost:${port:-8080}}"

docker compose ps --format 'table {{.Service}}\t{{.Status}}'
unhealthy="$(docker compose ps --all --format '{{.Service}} {{.Health}}' | awk '$2 != "healthy" {print $1}')"
if [[ -n "$unhealthy" ]]; then
  echo "not healthy: $(echo $unhealthy)" >&2
  exit 1
fi
python3 scripts/smoke_test.py --base "$base"
echo "verify: ok"
