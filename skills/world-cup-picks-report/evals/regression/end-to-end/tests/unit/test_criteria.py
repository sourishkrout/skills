from __future__ import annotations

import importlib.util
from pathlib import Path


CRITERIA_PATH = Path(__file__).parents[1] / "rewards" / "criteria.py"
SPEC = importlib.util.spec_from_file_location("criteria", CRITERIA_PATH)
assert SPEC is not None and SPEC.loader is not None
criteria = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(criteria)

ROLLUP_PATH = Path(__file__).parents[1] / "rollup_reward.py"
ROLLUP_SPEC = importlib.util.spec_from_file_location("rollup_reward", ROLLUP_PATH)
assert ROLLUP_SPEC is not None and ROLLUP_SPEC.loader is not None
rollup_reward = importlib.util.module_from_spec(ROLLUP_SPEC)
ROLLUP_SPEC.loader.exec_module(rollup_reward)


def read_fixture(path: str) -> str:
    return (Path(__file__).parents[1] / path).read_text()


def test_reward_rollup_uses_existing_emitted_scores(tmp_path: Path) -> None:
    reward_path = tmp_path / "reward.json"
    reward_path.write_text(
        "{\n"
        '  "artifact_written": 1.0,\n'
        '  "skill_activation_evidence": 1.0,\n'
        '  "citation_proximity": 0.5,\n'
        '  "scoreline_format": 0.5,\n'
        '  "guardrails": 1.0,\n'
        '  "target_slate_coverage": 0.75,\n'
        '  "report_completeness": 0.75,\n'
        '  "expert_anchor_coverage": 0.75,\n'
        '  "expert_anchor_usage": 0.5,\n'
        '  "source_quality": 0.75,\n'
        '  "workflow_sequence_evidence": 0.75\n'
        "}\n"
    )

    scores = rollup_reward.add_reward_rollup(reward_path)

    assert scores["reward"] == 0.75
    assert '"reward": 0.75' in reward_path.read_text()


def test_commands_from_atif() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [
          {"function_name": "exec_command", "arguments": {"cmd": "search web for FIFA fixtures"}},
          {"function_name": "Bash", "arguments": {"command": "search expert score prediction"}}
        ]
      }]
    }"""
    assert criteria.commands_from_atif(data) == [
        "search web for FIFA fixtures",
        "search expert score prediction",
    ]


def test_collect_agent_commands_from_file(tmp_path: Path) -> None:
    assert criteria.collect_agent_commands_from_file(tmp_path / "missing.json") == ""

    path = tmp_path / "trajectory.json"
    path.write_text('{"schema_version":"1.5","steps":[{"tool_calls":[{"function_name":"exec_command","arguments":{"cmd":"Search FIFA fixtures"}}]}]}')
    assert criteria.collect_agent_commands_from_file(path) == "search fifa fixtures"


def test_collect_agent_shell_trace_commands(tmp_path: Path) -> None:
    path = tmp_path / "oracle.txt"
    path.write_text(
        """Using world-cup-picks-report
+bad
 search without plus-space
+ search fifa fixtures
+ search expert score prediction
"""
    )

    got = criteria.collect_agent_shell_trace_commands_from_file(path)
    assert "search fifa fixtures" in got
    assert "search expert score prediction" in got
    assert "without plus-space" not in got


def test_skill_activation_from_atif_read_tool() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [{
          "function_name": "Read",
          "arguments": {
            "file_path": "/repo/.agents/skills/world-cup-picks-report/SKILL.md"
          }
        }]
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 1.0


def test_skill_activation_ignores_source_package_read() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [{
          "function_name": "Read",
          "arguments": {
            "file_path": "/repo/skills/world-cup-picks-report/SKILL.md"
          }
        }]
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 0.0


def test_skill_activation_from_atif_skill_tool() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [{
          "function_name": "Skill",
          "arguments": {"skill_name": "world-cup-picks-report"}
        }]
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 1.0


def test_skill_activation_from_atif_exec_command_reading_agent_skill_file() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [{
          "function_name": "exec_command",
          "arguments": {
            "cmd": "pwd && sed -n '1,240p' .agents/skills/world-cup-picks-report/SKILL.md"
          }
        }]
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 1.0


def test_skill_activation_ignores_file_listing_output() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [{
          "function_name": "Bash",
          "arguments": {"command": "find /repo -type f | head"}
        }],
        "observation": {
          "results": [{
            "content": "/repo/skills/world-cup-picks-report/SKILL.md"
          }]
        }
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 0.0


def test_skill_activation_ignores_exec_command_listing_agent_skill_file() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "tool_calls": [{
          "function_name": "exec_command",
          "arguments": {
            "cmd": "rg --files .agents/skills/world-cup-picks-report && find .agents/skills/world-cup-picks-report -maxdepth 2 -type f -print"
          }
        }]
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 0.0


def test_skill_activation_ignores_report_terms() -> None:
    data = b"""{
      "schema_version": "1.5",
      "steps": [{
        "source": "agent",
        "message": "Here is the expert scoreline report."
      }]
    }"""
    assert criteria.score_skill_activation_evidence(data) == 0.0


def test_oracle_run_from_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"agent":{"name":"oracle"}}')
    oracle_log_path = tmp_path / "missing-oracle.txt"
    assert criteria.is_oracle_run(config_path, oracle_log_path)


def test_non_oracle_run_from_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"agent":{"name":"claude-code"}}')
    oracle_log_path = tmp_path / "missing-oracle.txt"
    assert not criteria.is_oracle_run(config_path, oracle_log_path)


def test_oracle_run_from_sentinel_file(tmp_path: Path) -> None:
    config_path = tmp_path / "missing-config.json"
    oracle_log_path = tmp_path / "oracle.txt"
    oracle_log_path.write_text("oracle trace")
    assert criteria.is_oracle_run(config_path, oracle_log_path)


def test_missing_atif_non_oracle_fails(tmp_path: Path, monkeypatch) -> None:
    missing_trajectory = tmp_path / "agent" / "trajectory.json"
    missing_trajectory.parent.mkdir()
    config_path = tmp_path / "config.json"
    config_path.write_text('{"agent":{"name":"claude-code"}}')

    monkeypatch.setattr(criteria, "AGENT_LOG_DIR", missing_trajectory.parent)
    monkeypatch.setattr(criteria, "CONFIG_PATH", config_path)
    monkeypatch.setattr(criteria, "ORACLE_LOG_PATH", tmp_path / "agent" / "oracle.txt")

    assert criteria.score_skill_activation_from_logs() == 0.0


def test_missing_atif_oracle_passes(tmp_path: Path, monkeypatch) -> None:
    missing_trajectory = tmp_path / "agent" / "trajectory.json"
    missing_trajectory.parent.mkdir()
    oracle_log_path = tmp_path / "agent" / "oracle.txt"
    oracle_log_path.write_text("oracle trace")

    monkeypatch.setattr(criteria, "AGENT_LOG_DIR", missing_trajectory.parent)
    monkeypatch.setattr(criteria, "CONFIG_PATH", tmp_path / "missing-config.json")
    monkeypatch.setattr(criteria, "ORACLE_LOG_PATH", oracle_log_path)

    assert criteria.score_skill_activation_from_logs() == 1.0


def test_match_blocks() -> None:
    report = read_fixture("fixtures/strong-report/report.md")
    blocks = criteria.match_blocks(report)
    assert len(blocks) == 2
    for block in blocks:
        assert "basis:" in block.lower()
        assert "risk:" in block.lower()


def test_match_blocks_only_scoreline_picks_section() -> None:
    report = """Report scope: June 27, 2026

Scoreline Picks

- France vs Senegal: 3:1 - Confidence: Medium
  Basis: Expert anchor with citation (https://example.com/france-senegal).
  Risk: Lineup checks.

- Iraq vs Norway: 0:3 - Confidence: Medium
  Basis: Expert anchor with citation (https://example.com/iraq-norway).
  Risk: Deep block.

- Austria vs Jordan: 3:0 - Confidence: Medium
  Basis: Expert anchor: Example publishes Austria 3-0 Jordan, while another Austria vs Jordan source gives 2:0 as the correct-score angle (https://example.com/austria-jordan).
  Risk: Fitness checks.

Best Scoreline Leans
- Iraq vs Norway 0:3: cleanest blend of sources.
- France vs Senegal 3:1: strong favorite but not automatic.

Wait For Lineups
- France vs Senegal: check availability.
"""
    blocks = criteria.match_blocks(report)
    assert len(blocks) == 3
    for block in blocks:
        assert "Best Scoreline Leans" not in block
        assert "cleanest blend" not in block
        assert not block.startswith("Basis:")


def test_match_blocks_accepts_pick_headings() -> None:
    report = """Report scope: Saturday, June 27, 2026.

## Scoreline Picks

### France vs Senegal: 2:1 - Confidence: Medium
Basis: Expert anchor with citation (https://example.com/france-senegal).
Risk: Senegal counterattacks.

### Iraq vs Norway: 0:2 - Confidence: High
Basis: Expert anchor with citation (https://example.com/iraq-norway).
Risk: Low block.

## Best Scoreline Leans
- Iraq vs Norway 0:2
"""
    blocks = criteria.match_blocks(report)
    assert len(blocks) == 2
    assert blocks[0].startswith("### France vs Senegal: 2:1")
    assert criteria.score_scoreline_format(blocks) == 1.0


def test_centralized_source_traceability() -> None:
    report = """Report scope: Group stage matchday, Saturday, June 27, 2026.

## Scoreline Picks

### France vs Senegal: 2:1 - Confidence: Medium
Basis: Opta makes France the clear favorite, Dimers is similar, and Football Whispers leans France 3-1.
Risk: Senegal are stronger than a typical underdog.

### Iraq vs Norway: 0:2 - Confidence: High
Basis: Dimers lists 2-0 as the most likely correct score, with ESPN market lines also making Norway a heavy favorite.
Risk: Iraq can sit deep.

## Best Scoreline Leans
- Iraq vs Norway 0:2

## Wait For Lineups
- France vs Senegal.

## Sources
- Opta France vs Senegal: https://theanalyst.com/articles/france-vs-senegal-prediction-world-cup-2026-match-preview
- Dimers score/probability pages: https://www.dimers.com/bet-hub/swc/schedule/2026_1_fra_sen, https://www.dimers.com/bet-hub/swc/schedule/2026_1_irq_nor
- ESPN schedule/market lines: https://www.espn.com/soccer/schedule/_/league/fifa.world
- Football Whispers: https://footballwhispers.com/blog/france-vs-senegal-prediction-betting-tips-preview-world-cup-2026/
"""
    blocks = criteria.match_blocks(report)
    assert criteria.score_citation_proximity(report, blocks) == 1.0


def test_vague_anchor_without_traceable_source_fails() -> None:
    report = """Report scope: Group stage matchday, Saturday, June 27, 2026.

## Scoreline Picks

### France vs Senegal: 2:1 - Confidence: Medium
Basis: Experts and the market support France.
Risk: Senegal are stronger than a typical underdog.

## Sources
- FIFA fixtures: https://www.fifa.com/
"""
    blocks = criteria.match_blocks(report)
    assert criteria.score_citation_proximity(report, blocks) == 0.0


def test_report_date_freshness() -> None:
    fresh = """# World Cup Scoreline Picks

Report scope: Wednesday, June 24, 2026 in U.S. Pacific time.

## Scoreline Picks

### France vs Senegal: 2:1 - Confidence: Medium
Basis: Expert anchor, model, market, and Elo checks.
Risk: Lineups.
"""
    stale = fresh.replace("Wednesday, June 24, 2026", "Tuesday, June 23, 2026")
    assert criteria.score_report_date_freshness(fresh)
    assert not criteria.score_report_date_freshness(stale)


def test_resolve_target_slate_uses_next_future_fixture_date() -> None:
    slate = criteria.resolve_target_slate()

    assert slate["as_of_date"].isoformat() == "2026-06-23"
    assert slate["earliest_date"].isoformat() == "2026-06-24"
    assert slate["date"].isoformat() == "2026-06-24"
    assert len(slate["fixtures"]) == 6


def test_resolve_target_slate_skips_same_day_fixtures() -> None:
    slate = criteria.resolve_target_slate(as_of_override="2026-06-22")

    assert slate["earliest_date"].isoformat() == "2026-06-23"
    assert slate["date"].isoformat() == "2026-06-23"
    assert [fixture["home"] for fixture in slate["fixtures"]] == ["Spain"]


def test_resolve_target_slate_accepts_tomorrow(tmp_path: Path) -> None:
    schedule = tmp_path / "schedule.json"
    schedule.write_text(
        """{
          "as_of_date_pt": "2026-06-23",
          "fixtures": [
            {"date_pt": "2026-06-24", "time_pt": "12:00", "home": "France", "away": "Senegal", "group": "A"}
          ]
        }"""
    )

    slate = criteria.resolve_target_slate(schedule)

    assert slate["date"].isoformat() == "2026-06-24"


def test_resolve_target_slate_raises_without_future_fixtures(tmp_path: Path) -> None:
    schedule = tmp_path / "schedule.json"
    schedule.write_text(
        """{
          "as_of_date_pt": "2026-06-23",
          "fixtures": [
            {"date_pt": "2026-06-23", "time_pt": "12:00", "home": "France", "away": "Senegal", "group": "A"}
          ]
        }"""
    )

    try:
        criteria.resolve_target_slate(schedule)
    except ValueError as exc:
        assert "No fixtures found" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_target_slate_coverage_full_report() -> None:
    report = """Report scope: Wednesday, June 24, 2026 in U.S. Pacific time.

## Scoreline Picks

### Switzerland vs Canada: 1:1 - Confidence: Low
Basis: Expert anchor.
Risk: Game state.

### Bosnia-Herzegovina vs Qatar: 2:0 - Confidence: Medium
Basis: Expert anchor.
Risk: Volatility.

### Scotland vs Brazil: 0:2 - Confidence: Medium
Basis: Expert anchor.
Risk: Rotation.

### Morocco vs Haiti: 2:0 - Confidence: High
Basis: Expert anchor.
Risk: Rotation.

### Czechia vs Mexico: 0:1 - Confidence: Medium
Basis: Expert anchor.
Risk: Draw.

### South Africa vs South Korea: 0:1 - Confidence: Medium
Basis: Expert anchor.
Risk: Suspensions.
"""

    assert criteria.score_target_slate_coverage(report) == 1.0


def test_target_slate_coverage_accepts_team_aliases() -> None:
    report = """Report scope: Wednesday, June 24, 2026 in U.S. Pacific time.

## Scoreline Picks

### Switzerland vs Canada: 1:1 - Confidence: Low
### Bosnia and Herzegovina vs Qatar: 2:0 - Confidence: Medium
### Scotland vs Brazil: 0:2 - Confidence: Medium
### Morocco vs Haiti: 2:0 - Confidence: High
### Czech Republic vs Mexico: 0:1 - Confidence: Medium
### South Africa vs Korea Republic: 0:1 - Confidence: Medium
"""

    assert criteria.score_target_slate_coverage(report) == 1.0


def test_target_slate_coverage_penalizes_missing_fixture() -> None:
    report = """Report scope: Wednesday, June 24, 2026 in U.S. Pacific time.

## Scoreline Picks

### Switzerland vs Canada: 1:1 - Confidence: Low
### Bosnia-Herzegovina vs Qatar: 2:0 - Confidence: Medium
### Scotland vs Brazil: 0:2 - Confidence: Medium
### Morocco vs Haiti: 2:0 - Confidence: High
### Czechia vs Mexico: 0:1 - Confidence: Medium
"""

    assert criteria.score_target_slate_coverage(report) < 1.0


def test_target_slate_coverage_rejects_stale_or_same_day_scope() -> None:
    stale = """Report scope: Tuesday, June 23, 2026 in U.S. Pacific time.

## Scoreline Picks

### Spain vs Uruguay: 1:1 - Confidence: Medium
"""

    assert criteria.score_target_slate_coverage(stale) == 0.0


def test_target_slate_coverage_penalizes_missing_pacific_framing() -> None:
    report = """Report scope: Wednesday, June 24, 2026.

## Scoreline Picks

### Switzerland vs Canada: 1:1 - Confidence: Low
### Bosnia-Herzegovina vs Qatar: 2:0 - Confidence: Medium
### Scotland vs Brazil: 0:2 - Confidence: Medium
### Morocco vs Haiti: 2:0 - Confidence: High
### Czechia vs Mexico: 0:1 - Confidence: Medium
### South Africa vs South Korea: 0:1 - Confidence: Medium
"""

    assert criteria.score_target_slate_coverage(report) == 0.85


def test_guardrails() -> None:
    assert criteria.score_guardrails("This is guaranteed and you should bet 10% of bankroll.") == 0.0
    assert criteria.score_guardrails("This is informational and not guaranteed.") == 1.0
    assert criteria.score_guardrails("No guaranteed result here; this is informational.") == 1.0
    assert criteria.score_guardrails("Don't read Argentina's friendly blowouts as a guaranteed rout.") == 1.0
    assert criteria.score_guardrails("This scoreline is guaranteed.") == 0.0
    assert criteria.score_guardrails("Do not present this as a certainty. No wagering advice.") == 1.0
