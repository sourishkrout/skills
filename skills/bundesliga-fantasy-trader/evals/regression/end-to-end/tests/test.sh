#!/bin/bash
set -euo pipefail

verifier_dir="${RUNME_VERIFIER_DIR:-/logs/verifier}"
reward_path="${RUNME_REWARD_PATH:-$verifier_dir/reward.json}"
stdout_path="$verifier_dir/test-stdout.txt"

mkdir -p "$verifier_dir"

{
  echo "Verifier started for ${RUNME_TASK_NAME:-bundesliga-fantasy-trader_end-to-end}"
  echo "Task workdir: ${RUNME_TASK_WORKDIR:-/app/evals/regression/end-to-end/workdir}"
  echo
  echo "Checking stub success condition: implement real checks before expecting this task to pass"

  # Harbor expects the canonical reward JSON to be a reward-name-to-score map.
  printf '{"reward": 0.0}\n' > "$reward_path"

  echo "Reward written to: $reward_path"
  echo "Reward: 0.0"
  echo
  echo "Verifier completed successfully"
} | tee "$stdout_path"
