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
# Older releases predate private documents (they would serve them to anyone) and run workers.
# Only releases from the run-worker change (66e3a1d) on match this database and Compose file.
if ! git rev-parse --verify --quiet "${tag}^{commit}" > /dev/null ||
  ! git merge-base --is-ancestor 66e3a1d "${tag}^{commit}"; then
  echo "rollback refused: ${tag} predates private documents and run workers" >&2
  exit 1
fi
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
