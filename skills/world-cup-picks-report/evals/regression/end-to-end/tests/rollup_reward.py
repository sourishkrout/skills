from __future__ import annotations

import json
import sys
from pathlib import Path


ROLLUP_KEYS = (
    "artifact_written",
    "skill_activation_evidence",
    "citation_proximity",
    "scoreline_format",
    "guardrails",
    "target_slate_coverage",
    "report_completeness",
    "expert_anchor_coverage",
    "expert_anchor_usage",
    "source_quality",
    "workflow_sequence_evidence",
)


def add_reward_rollup(path: Path) -> dict[str, float]:
    scores = json.loads(path.read_text())
    missing = [key for key in ROLLUP_KEYS if key not in scores]
    if missing:
        raise KeyError(
            f"Cannot compute reward rollup; missing scores: {', '.join(missing)}"
        )

    total = sum(float(scores[key]) for key in ROLLUP_KEYS)
    scores["reward"] = round(total / len(ROLLUP_KEYS), 4)
    path.write_text(json.dumps(scores, indent=2) + "\n")
    return scores


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: rollup_reward.py /path/to/reward.json")
    add_reward_rollup(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
