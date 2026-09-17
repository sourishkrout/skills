from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path


TESTS_DIR = Path(__file__).parents[1]
REWARDS_DIR = TESTS_DIR / "rewards"
CRITERIA_PATH = REWARDS_DIR / "criteria.py"
SPEC = importlib.util.spec_from_file_location("bundesliga_criteria", CRITERIA_PATH)
assert SPEC is not None and SPEC.loader is not None
criteria = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(criteria)

ROLLUP_PATH = TESTS_DIR / "rollup_reward.py"
ROLLUP_SPEC = importlib.util.spec_from_file_location("bundesliga_rollup", ROLLUP_PATH)
assert ROLLUP_SPEC is not None and ROLLUP_SPEC.loader is not None
rollup = importlib.util.module_from_spec(ROLLUP_SPEC)
ROLLUP_SPEC.loader.exec_module(rollup)


def fixture(name: str, filename: str) -> str:
    return (TESTS_DIR / "fixtures" / name / filename).read_text()


def registered_criteria_for_reward(name: str) -> list[tuple[str, float]]:
    from rewardkit import session

    session.current().clear()
    path = REWARDS_DIR / name / "score.py"
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
    assert registered_criteria_for_reward("artifact_written") == [
        ("report_artifact_written", 1.0)
    ]
    assert registered_criteria_for_reward("offline_evidence_boundary") == [
        ("no_external_network_use", 1.0)
    ]
    assert registered_criteria_for_reward("skill_activation_evidence") == [
        ("activation_log_present", 0.0),
        ("read_tool_used", 0.0),
        ("skill_tool_used", 0.0),
        ("exec_tool_used", 0.0),
        ("bundesliga_skill_activation_detected", 1.0),
    ]


def test_report_rewards_are_semantic_judges() -> None:
    for name in (
        "temporal_integrity",
        "task_contract",
        "budget_and_state_safety",
        "decision_quality",
        "evidence_quality",
    ):
        directory = REWARDS_DIR / name
        assert not (directory / "score.py").exists()
        config = tomllib.loads((directory / "judge.toml").read_text())
        assert "/logs/artifacts/report.md" in config["judge"]["files"]
        assert config["criterion"][0]["type"] == "likert"
        assert config["criterion"][0]["points"] == 5


def test_artifact_written_requires_nonempty_report() -> None:
    assert criteria.score_artifact_written("# Report\n") == 1.0
    assert criteria.score_artifact_written("  \n") == 0.0


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


def test_skill_activation_from_claude_read_tool() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "Read",
        "arguments": {"file_path": "/app/workdir/.claude/skills/bundesliga-fantasy-trader/SKILL.md"}
      }]}]
    }"""
    assert criteria.score_skill_activation_evidence(trajectory) == 1.0


def test_skill_activation_from_exec_wrappers() -> None:
    for name in ("luna-exec-activation", "sol-exec-activation"):
        assert criteria.score_skill_activation_evidence(
            fixture(name, "trajectory.json")
        ) == 1.0


def test_skill_activation_ignores_source_package_read() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "Read",
        "arguments": {"file_path": "/repo/skills/bundesliga-fantasy-trader/SKILL.md"}
      }]}]
    }"""
    assert criteria.score_skill_activation_evidence(trajectory) == 0.0


def test_skill_activation_ignores_listing_and_patch_mentions() -> None:
    listing = """{
      "steps": [{"tool_calls": [{
        "function_name": "exec_command",
        "arguments": {"cmd": "rg --files .agents/skills/bundesliga-fantasy-trader"}
      }]}]
    }"""
    patch = """{
      "steps": [{"tool_calls": [{
        "function_name": "exec",
        "arguments": {"input": "await tools.apply_patch('Mention .agents/skills/bundesliga-fantasy-trader/SKILL.md and sed in prose')"}
      }]}]
    }"""
    assert criteria.score_skill_activation_evidence(listing) == 0.0
    assert criteria.score_skill_activation_evidence(patch) == 0.0


def test_skill_activation_ignores_snapshot_read_and_malformed_trajectory() -> None:
    snapshot_read = """{
      "steps": [{"tool_calls": [{
        "function_name": "exec_command",
        "arguments": {"cmd": "sed -n '1,240p' snapshot/evidence.md"}
      }]}]
    }"""
    assert criteria.score_skill_activation_evidence(snapshot_read) == 0.0
    assert criteria.score_skill_activation_evidence("not json") == 0.0


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


def test_wrapped_web_tool_fails_offline_evidence_boundary() -> None:
    trajectory = """{
      "steps": [{"tool_calls": [{
        "function_name": "exec",
        "arguments": {"input": "const r = await tools.web__run({search_query:[{q:'Matchday 4 results'}]});"}
      }]}]
    }"""
    assert criteria.score_no_external_network_use(trajectory) == 0.0


def test_wrapped_curl_and_wget_fail_offline_evidence_boundary() -> None:
    for command in ("curl https://example.com", "wget https://example.com"):
        trajectory = """{
          "steps": [{"tool_calls": [{
            "function_name": "exec",
            "arguments": {"input": "const r = await tools.exec_command({cmd: %s});"}
          }]}]
        }""" % repr(command)
        assert criteria.score_no_external_network_use(trajectory) == 0.0


def test_wrapped_local_read_and_plain_url_respect_offline_boundary() -> None:
    trajectory = json.dumps(
        {
            "steps": [
                {
                    "tool_calls": [
                        {
                            "function_name": "exec",
                            "arguments": {
                                "input": "const r = await tools.exec_command({cmd: \"sed -n '1,40p' snapshot/evidence.md && rg 'https://example.com' report.md\"});"
                            },
                        }
                    ]
                }
            ]
        }
    )
    assert criteria.score_no_external_network_use(trajectory) == 1.0


def test_malformed_trajectory_fails_offline_boundary() -> None:
    assert criteria.score_no_external_network_use("not json") == 0.0


def test_reward_rollup_full_score(tmp_path: Path) -> None:
    reward_path = tmp_path / "reward.json"
    reward_path.write_text(json.dumps({key: 1.0 for key in rollup.ROLLUP_KEYS}))
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 1.0


def test_reward_rollup_averages_semantic_deductions(tmp_path: Path) -> None:
    values = {key: 1.0 for key in rollup.ROLLUP_KEYS}
    values["temporal_integrity"] = 0.8
    values["budget_and_state_safety"] = 0.75
    reward_path = tmp_path / "reward.json"
    reward_path.write_text(json.dumps(values))
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 0.9437


def test_reward_rollup_includes_offline_boundary(tmp_path: Path) -> None:
    values = {key: 1.0 for key in rollup.ROLLUP_KEYS}
    values["offline_evidence_boundary"] = 0.0
    reward_path = tmp_path / "reward.json"
    reward_path.write_text(json.dumps(values))
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 0.875


def test_reward_rollup_zeroes_missing_artifact(tmp_path: Path) -> None:
    values = {key: 1.0 for key in rollup.ROLLUP_KEYS}
    values["artifact_written"] = 0.0
    reward_path = tmp_path / "reward.json"
    reward_path.write_text(json.dumps(values))
    scores = rollup.add_reward_rollup(reward_path)
    assert scores["reward"] == 0.0
