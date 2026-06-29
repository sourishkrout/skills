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


def registered_criteria_for_reward(name: str) -> list[tuple[str, float]]:
    from rewardkit import session

    session.current().clear()
    path = Path(__file__).parents[1] / "rewards" / name / "score.py"
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


def test_programmatic_rewards_register_dashboard_breakouts() -> None:
    assert registered_criteria_for_reward("artifact_written") == [
        ("report_file_exists", 1.0),
        ("report_file_nonempty", 2.0),
    ]
    assert registered_criteria_for_reward("citation_proximity") == [
        ("report_has_url", 0.0),
        ("report_has_source_terms", 0.0),
        ("match_blocks_have_traceable_citations", 1.0),
    ]
    assert registered_criteria_for_reward("guardrails") == [
        ("banned_wagering_terms_absent", 1.0),
        ("unnegated_guaranteed_absent", 1.0),
    ]
    assert registered_criteria_for_reward("scoreline_format") == [
        ("scoreline_picks_section_present", 1.0),
        ("scoreline_pattern_present", 1.0),
        ("match_pick_headings_include_scorelines", 3.0),
    ]
    assert registered_criteria_for_reward("skill_activation_evidence") == [
        ("activation_log_present", 0.0),
        ("read_tool_used", 0.0),
        ("skill_tool_used", 0.0),
        ("world_cup_skill_activation_detected", 1.0),
    ]
    assert registered_criteria_for_reward("target_slate_coverage") == [
        ("target_scope_date_present", 0.0),
        ("target_pacific_framing_present", 0.0),
        ("target_fixture_mentions", 0.0),
        ("target_slate_weighted_coverage", 1.0),
    ]
    assert registered_criteria_for_reward("lineup_status") == [
        ("lineup_status_confirmed_or_materially_pending", 1.0),
    ]


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
        '  "lineup_status": 1.0,\n'
        '  "report_completeness": 0.75,\n'
        '  "expert_anchor_coverage": 0.75,\n'
        '  "expert_anchor_usage": 0.5,\n'
        '  "source_quality": 0.75,\n'
        '  "workflow_sequence_evidence": 0.75\n'
        "}\n"
    )

    scores = rollup_reward.add_reward_rollup(reward_path)

    assert scores["reward"] == 0.7708
    assert '"reward": 0.7708' in reward_path.read_text()


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


def test_match_blocks_stops_at_lineup_status_section() -> None:
    report = """Report scope: Saturday, June 27, 2026.

## Scoreline Picks

### France vs Senegal: 2:1 - Confidence: Medium
Basis: Expert anchor with citation (https://example.com/france-senegal).
Risk: Senegal counterattacks.

## Lineup Status
- Lineups checked: France start their first-choice front three; no change to 2:1.

## Sources
- FIFA: https://www.fifa.com/
"""
    blocks = criteria.match_blocks(report)
    assert len(blocks) == 1
    assert "Lineup Status" not in blocks[0]


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


def test_target_slate_coverage_full_declared_knockout_report() -> None:
    report = """Report scope: FIFA World Cup 2026 Round of 32, Tuesday, June 30, 2026 in U.S. Pacific time. This is the next full unplayed slate no earlier than tomorrow from the current runtime date of Monday, June 29, 2026 PT.

## Scoreline Picks

### Cote d'Ivoire vs Norway: 1:2 - Aggregate incl. PKs: 1:2 - Confidence: Medium
90-min score: Cote d'Ivoire 1:2 Norway
AET/PK outcome: Norway advances in regulation.
PK likelihood: Low - draw-after-90 is modest.

### France vs Sweden: 3:1 - Aggregate incl. PKs: 3:1 - Confidence: Medium
90-min score: France 3:1 Sweden
AET/PK outcome: France advances in regulation.
PK likelihood: Low - favorite edge is large.

### Mexico vs Ecuador: 2:1 - Aggregate incl. PKs: 2:1 - Confidence: Low
90-min score: Mexico 2:1 Ecuador
AET/PK outcome: Mexico advances in regulation.
PK likelihood: Medium - narrow Elo gap and higher draw-after-90.
"""

    assert criteria.score_target_slate_coverage(report) == 1.0


def test_target_slate_coverage_partial_for_one_declared_scored_fixture() -> None:
    report = """Report scope: Tuesday, June 30, 2026 in U.S. Pacific time.

## Scoreline Picks

### France vs Sweden: 3:1 - Confidence: Medium
"""

    assert criteria.score_target_slate_coverage(report) == 0.6667


def test_target_slate_coverage_requires_selected_slate_date() -> None:
    report = """Report scope: next full unplayed World Cup slate in U.S. Pacific time.

## Scoreline Picks

### Cote d'Ivoire vs Norway: 1:2 - Confidence: Medium
### France vs Sweden: 3:1 - Confidence: Medium
### Mexico vs Ecuador: 2:1 - Confidence: Low
"""

    assert criteria.score_target_slate_coverage(report) == 0.75


def test_target_slate_coverage_penalizes_unscored_fixture_blocks() -> None:
    report = """Report scope: Tuesday, June 30, 2026 in U.S. Pacific time.

## Scoreline Picks

### Cote d'Ivoire vs Norway: 1:2 - Confidence: Medium
### France vs Sweden - Confidence: Medium
### Mexico vs Ecuador - Confidence: Low
"""

    assert criteria.score_target_slate_coverage(report) == 0.6667


def test_target_slate_coverage_dedupes_repeated_scored_fixture() -> None:
    report = """Report scope: Tuesday, June 30, 2026 in U.S. Pacific time.

## Scoreline Picks

### France vs Sweden: 3:1 - Confidence: Medium
### France vs Sweden: 2:1 - Confidence: Medium
### France vs Sweden: 1:0 - Confidence: Low
"""

    assert criteria.score_target_slate_coverage(report) == 0.6667


def test_target_slate_coverage_rejects_internal_stale_scope_conflict() -> None:
    report = """Report scope: Tuesday, June 23, 2026 in U.S. Pacific time from the current runtime date of Tuesday, June 23, 2026 PT.

## Scoreline Picks

### Spain vs Uruguay: 1:1 - Confidence: Medium
### France vs Senegal: 2:1 - Confidence: Medium
### Brazil vs Scotland: 2:0 - Confidence: Medium
"""

    assert criteria.score_target_slate_coverage(report) == 0.9


def test_target_slate_coverage_penalizes_missing_pacific_framing() -> None:
    report = """Report scope: Tuesday, June 30, 2026.

## Scoreline Picks

### Cote d'Ivoire vs Norway: 1:2 - Confidence: Medium
### France vs Sweden: 3:1 - Confidence: Medium
### Mexico vs Ecuador: 2:1 - Confidence: Low
"""

    assert criteria.score_target_slate_coverage(report) == 0.85


def test_lineup_status_accepts_confirmed_lineups() -> None:
    report = """## Lineup Status
- Lineups checked: Norway start Haaland, Odegaard, and Sorloth; no change to 2:1 Norway.
"""

    assert criteria.score_lineup_status_actionable(report) == 1.0


def test_lineup_status_accepts_material_pending_lineups() -> None:
    report = """## Lineup Status
- Lineups pending: wait on Mexico striker and keeper because it affects confidence and the 1:1 vs 2:1 scoreline.
"""

    assert criteria.score_lineup_status_actionable(report) == 1.0


def test_lineup_status_accepts_future_unavailable_lineups_with_material_checks() -> None:
    report = """## Lineup Status
Projected-lineup and team-news context incorporated; confirmed starting XIs are not available this far out. Material checks: William Saliba's France return/status, Ivory Coast's Singo and Amad Diallo availability, and Norway's Ryerson fitness.
"""

    assert criteria.score_lineup_status_actionable(report) == 1.0


def test_lineup_status_accepts_future_unavailable_lineups_with_no_material_questions() -> None:
    report = """## Lineup Status
Confirmed XIs are not yet available; no material lineup questions move the pick.
"""

    assert criteria.score_lineup_status_actionable(report) == 1.0


def test_lineup_status_rejects_generic_wait_only() -> None:
    report = """## Wait For Lineups
- France vs Senegal: watch final lineups.
"""

    assert criteria.score_lineup_status_actionable(report) == 0.0


def test_lineup_status_rejects_missing_section() -> None:
    report = """## Scoreline Picks
### France vs Senegal: 2:1 - Confidence: Medium
Risk: Watch final lineups for France.
"""

    assert criteria.score_lineup_status_actionable(report) == 0.0


def test_guardrails() -> None:
    assert criteria.score_guardrails("This is guaranteed and you should bet 10% of bankroll.") == 0.0
    assert criteria.score_guardrails("This is informational and not guaranteed.") == 1.0
    assert criteria.score_guardrails("No guaranteed result here; this is informational.") == 1.0
    assert criteria.score_guardrails("Don't read Argentina's friendly blowouts as a guaranteed rout.") == 1.0
    assert criteria.score_guardrails("This scoreline is guaranteed.") == 0.0
    assert criteria.score_guardrails("Do not present this as a certainty. No wagering advice.") == 1.0
