#!/usr/bin/env bash
# Deploy the current commit: build images tagged with its short SHA, start them, verify.
#   scripts/deploy.sh            # deploy HEAD
# The previous tag is kept in .deploy/previous for scripts/rollback.sh.
set -euo pipefail
cd "$(dirname "$0")/.."

tag="$(git rev-parse --short HEAD)"
mkdir -p .deploy
if [[ -f .deploy/current ]]; then cp .deploy/current .deploy/previous; fi

echo "building images agentic-rag-*:${tag}"
IMAGE_TAG="$tag" docker compose build
echo "starting ${tag}"
IMAGE_TAG="$tag" docker compose up -d --wait --wait-timeout 240
echo "$tag" > .deploy/current

scripts/verify.sh
echo "deployed ${tag} (previous: $(cat .deploy/previous 2>/dev/null || echo none))"
