from __future__ import annotations

import json
import sys
from pathlib import Path


ROLLUP_KEYS = (
    "artifact_written",
    "skill_activation_evidence",
    "temporal_integrity",
    "task_contract",
    "budget_and_state_safety",
    "decision_quality",
    "evidence_quality",
)


def add_reward_rollup(path: Path) -> dict[str, float]:
    scores = json.loads(path.read_text())
    missing = [key for key in ROLLUP_KEYS if key not in scores]
    if missing:
        raise KeyError(f"Cannot compute reward rollup; missing scores: {', '.join(missing)}")

    reward = sum(float(scores[key]) for key in ROLLUP_KEYS) / len(ROLLUP_KEYS)
    if float(scores["artifact_written"]) <= 0:
        reward = 0.0

    scores["reward"] = round(reward, 4)
    path.write_text(json.dumps(scores, indent=2) + "\n")
    return scores


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: rollup_reward.py /path/to/reward.json")
    add_reward_rollup(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
