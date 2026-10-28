#!/usr/bin/env bash
# Roll back to the previously deployed image tag (or a given one) without rebuilding.
#   scripts/rollback.sh          # back to .deploy/previous
#   scripts/rollback.sh abc1234  # to a specific tag that still exists locally
# Database migrations are additive (new tables and columns only), so older code runs on the
# newer schema; data is never rolled back.
set -euo pipefail
cd "$(dirname "$0")/.."

tag="${1:-$(cat .deploy/previous 2>/dev/null || true)}"
if [[ -z "$tag" ]]; then echo "no previous deployment recorded; pass a tag" >&2; exit 1; fi
for image in callslip-backend callslip-frontend; do
  docker image inspect "${image}:${tag}" > /dev/null || { echo "missing ${image}:${tag}" >&2; exit 1; }
done

current="$(cat .deploy/current 2>/dev/null || true)"
echo "rolling back to ${tag}"
IMAGE_TAG="$tag" docker compose up -d --no-build --wait --wait-timeout 240
scripts/verify.sh
# Recorded only after verification, like deploy.sh.
if [[ -n "$current" && "$current" != "$tag" ]]; then echo "$current" > .deploy/previous; fi
echo "$tag" > .deploy/current
echo "running ${tag}"
