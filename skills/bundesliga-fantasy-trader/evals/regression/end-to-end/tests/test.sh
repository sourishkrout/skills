#!/usr/bin/env sh
set -eu

verifier_dir="${RUNME_VERIFIER_DIR:-/logs/verifier}"
reward_path="${RUNME_REWARD_PATH:-$verifier_dir/reward.json}"

mkdir -p "$verifier_dir"

uvx --quiet --from harbor-rewardkit rewardkit \
  --workspace /app \
  --output "$reward_path" \
  /tests/rewards \
  2> "$verifier_dir/uvx-stderr.txt"

uvx --quiet --from harbor-rewardkit python \
  /tests/rollup_reward.py "$reward_path"
