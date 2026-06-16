#!/usr/bin/env sh
set -eu

mkdir -p /logs/verifier
uvx --quiet --from harbor-rewardkit rewardkit \
  --workspace /app \
  --output /logs/verifier/reward.json \
  /tests/rewards \
  2> /logs/verifier/uvx-stderr.txt
