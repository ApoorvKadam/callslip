#!/usr/bin/env bash
# Deploy the current commit: build images tagged with its short SHA, start them, verify.
#   scripts/deploy.sh            # deploy HEAD
# The tag is recorded in .deploy/current only after verification passes; the one it replaces
# moves to .deploy/previous for scripts/rollback.sh.
set -euo pipefail
cd "$(dirname "$0")/.."

tag="$(git rev-parse --short HEAD)"
# The tag names a commit, so the images must be built from exactly that commit.
if [[ -n "$(git status --porcelain -- backend frontend docker-compose.yml)" ]]; then
  echo "uncommitted changes in backend, frontend or docker-compose.yml; commit them first" >&2
  exit 1
fi
mkdir -p .deploy
current="$(cat .deploy/current 2>/dev/null || true)"

echo "building images callslip-*:${tag}"
IMAGE_TAG="$tag" docker compose build
echo "starting ${tag}"
IMAGE_TAG="$tag" docker compose up -d --wait --wait-timeout 240

if ! scripts/verify.sh; then
  echo "verify failed for ${tag}; last verified: ${current:-none} (scripts/rollback.sh ${current})" >&2
  exit 1
fi
if [[ -n "$current" && "$current" != "$tag" ]]; then echo "$current" > .deploy/previous; fi
echo "$tag" > .deploy/current
echo "deployed ${tag} (previous: $(cat .deploy/previous 2>/dev/null || echo none))"
