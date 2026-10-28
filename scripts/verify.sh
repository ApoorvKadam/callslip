#!/usr/bin/env bash
# Verify a running stack: container health, API liveness and readiness, then an end-to-end
# upload, ingestion and search (scripts/smoke_test.py). Exits non-zero on any failure.
set -euo pipefail
cd "$(dirname "$0")/.."
base="${BASE_URL:-http://localhost:8080}"

docker compose ps --format 'table {{.Service}}\t{{.Status}}'
python3 scripts/smoke_test.py --base "$base"
echo "verify: ok"
