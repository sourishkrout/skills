from __future__ import annotations

import importlib.util
from pathlib import Path


TESTS_DIR = Path(__file__).parents[1]
CRITERIA_PATH = TESTS_DIR / "rewards" / "criteria.py"
SPEC = importlib.util.spec_from_file_location("bundesliga_criteria", CRITERIA_PATH)
assert SPEC is not None and SPEC.loader is not None
criteria = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(criteria)

ROLLUP_PATH = TESTS_DIR / "rollup_reward.py"
ROLLUP_SPEC = importlib.util.spec_from_file_location("bundesliga_rollup", ROLLUP_PATH)
assert ROLLUP_SPEC is not None and ROLLUP_SPEC.loader is not None
rollup = importlib.util.module_from_spec(ROLLUP_SPEC)
ROLLUP_SPEC.loader.exec_module(rollup)


def fixture(name: str, filename: str = "report.md") -> str:
    return (TESTS_DIR / "fixtures" / name / filename).read_text()


def registered_criteria_for_reward(name: str) -> list[tuple[str, float]]:
    from rewardkit import session

    session.current().clear()
    path = TESTS_DIR / "rewards" / name / "score.py"
    spec = importlib.util.spec_from_file_location(f"{name}_score", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    registered = [
        (getattr(fn, "_criterion_name", fn.__name__), weight)
        for fn, weight in session.current().criteria
    ]
    session.current().clear()
    return registered


def test_programmatic_rewards_register_expected_metrics() -> None:
    expected = {
        "artifact_written": "report_artifact_written",
        "skill_activation_evidence": "bundesliga_skill_activation_detected",
        "temporal_integrity": "frozen_cutoff_respected",
        "task_contract": "matchday_plan_contract_satisfied",
        "budget_and_state_safety": "budget_and_state_handled_safely",
    }
    for reward, criterion_name in expected.items():
        assert registered_criteria_for_reward(reward) == [(criterion_name, 1.0)]


def test_strong_report_satisfies_programmatic_contracts() -> None:
    report = fixture("strong-report")
    assert criteria.score_temporal_integrity(report) == 1.0
    assert criteria.score_task_contract(report) == 1.0
    assert criteria.score_budget_and_state_safety(report) == 1.0


def test_hindsight_and_post_cutoff_sources_fail_temporal_integrity() -> None:
    report = fixture("hindsight-report")
    assert criteria.has_unexpected_scoreline(report)
    assert criteria.has_post_cutoff_source_date(report)
    assert criteria.score_temporal_integrity(report) < 1.0


def test_missing_fallback_fails_task_contract() -> None:
    assert criteria.score_task_contract(fixture("missing-fallback-report")) < 1.0


def test_invented_values_fail_budget_safety_shape() -> None:
    assert criteria.score_budget_and_state_safety(fixture("invented-values-report")) < 0.5


def test_skill_activation_from_skill_tool() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "Skill",
        "arguments": {"skill_name": "bundesliga-fantasy-trader"}
      }]}]
    }"""
    assert criteria.score_skill_activation_evidence(trajectory) == 1.0


def test_skill_activation_from_injected_skill_read() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "exec_command",
        "arguments": {"cmd": "sed -n '1,240p' /app/workdir/.agents/skills/bundesliga-fantasy-trader/SKILL.md"}
      }]}]
    }"""
    assert criteria.score_skill_activation_evidence(trajectory) == 1.0


def test_skipped_workflow_has_no_activation() -> None:
    data = fixture("skipped-workflow", "trajectory.json")
    assert criteria.score_skill_activation_evidence(data) == 0.0


def test_external_web_tool_fails_offline_evidence_boundary() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "web_search",
        "arguments": {"query": "Matchday 4 results"}
      }]}]
    }"""
    assert criteria.score_no_external_network_use(trajectory) == 0.0


def test_local_file_reads_respect_offline_evidence_boundary() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "exec_command",
        "arguments": {"cmd": "sed -n '1,240p' snapshot/evidence.md"}
      }]}]
    }"""
    assert criteria.score_no_external_network_use(trajectory) == 1.0


def test_reward_rollup_full_score(tmp_path: Path) -> None:
    reward_path = tmp_path / "reward.json"
    reward_path.write_text(
        "{" + ",".join(f'\"{key}\": 1.0' for key in rollup.ROLLUP_KEYS) + "}"
    )
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 1.0


def test_reward_rollup_caps_temporal_failure(tmp_path: Path) -> None:
    values = {key: 1.0 for key in rollup.ROLLUP_KEYS}
    values["temporal_integrity"] = 0.8
    reward_path = tmp_path / "reward.json"
    import json

    reward_path.write_text(json.dumps(values))
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 0.5


def test_reward_rollup_zeroes_missing_artifact(tmp_path: Path) -> None:
    values = {key: 1.0 for key in rollup.ROLLUP_KEYS}
    values["artifact_written"] = 0.0
    reward_path = tmp_path / "reward.json"
    import json

    reward_path.write_text(json.dumps(values))
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 0.0
