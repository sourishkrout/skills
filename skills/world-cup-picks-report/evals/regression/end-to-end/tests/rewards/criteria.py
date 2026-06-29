from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from rewardkit import criterion


AGENT_LOG_DIR = Path("/logs/agent")
ARTIFACTS_DIR = Path("/logs/artifacts")
CONFIG_PATH = Path("/logs/config.json")
ORACLE_LOG_PATH = AGENT_LOG_DIR / "oracle.txt"
REPORT_PATH = ARTIFACTS_DIR / "report.md"
FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"
SCHEDULE_PATH = FIXTURES_DIR / "world_cup_2026_schedule.json"
AS_OF_DATE_ENV = "WORLD_CUP_REPORT_AS_OF_DATE"

SCORELINE_RE = re.compile(r"\b\d+\s*:\s*\d+\b")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
VS_LINE_RE = re.compile(r"\b[0-9A-Za-z][^:\n]{1,100}\s+vs\.?\s+[^:\n]{1,100}", re.I)
DATE_RE = re.compile(
    r"\b(?:(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday),\s*)?"
    r"(?:january|february|march|april|may|june|july|august|september|october|"
    r"november|december)\s+\d{1,2},\s+2026\b",
    re.I,
)
PT_RE = re.compile(r"\b(?:pt|p\.?t\.?|pacific|u\.s\.\s+pacific)\b", re.I)

ANCHOR_NAMES = (
    "opta",
    "the analyst",
    "dimers",
    "football whispers",
    "sportsgambler",
    "sports gambler",
    "racing post",
    "livescore",
    "espn",
    "draftkings",
    "fox",
    "oddschecker",
    "world football elo",
    "elo ratings",
)
GENERIC_ANCHOR_TERMS = (
    "expert anchor",
    "expert pick",
    "expert prediction",
    "correct-score",
    "correct score",
    "score prediction",
    "preview",
    "prediction",
)
TEAM_ALIASES = {
    "bosnia-herzegovina": ("bosnia-herzegovina", "bosnia and herzegovina", "bosnia"),
    "czechia": ("czechia", "czech republic"),
    "dr congo": ("dr congo", "congo dr", "d.r. congo", "democratic republic of congo"),
    "south korea": ("south korea", "korea republic"),
}


@criterion(shared=True)
def artifact_written(workspace: Path) -> float:
    return score_artifact_written(read_report())


@criterion(shared=True)
def skill_activation_evidence(workspace: Path) -> float:
    return score_skill_activation_from_logs()


def score_skill_activation_from_logs() -> float:
    trajectory = read_text(AGENT_LOG_DIR / "trajectory.json")
    if trajectory:
        return score_skill_activation_evidence(trajectory)
    return 1.0 if is_oracle_run() else 0.0


@criterion(shared=True)
def citation_proximity(workspace: Path) -> float:
    report = read_report()
    return score_citation_proximity(report, match_blocks(report))


@criterion(shared=True)
def citation_proximity_by_match(workspace: Path) -> float:
    report = read_report()
    return score_citation_proximity(report, match_blocks(report))


@criterion(shared=True)
def scoreline_format(workspace: Path) -> float:
    return score_scoreline_format(match_blocks(read_report()))


@criterion(shared=True)
def parsed_scoreline_format(workspace: Path) -> float:
    return score_scoreline_format(match_blocks(read_report()))


@criterion(shared=True)
def guardrails(workspace: Path) -> float:
    return score_guardrails(read_report())


@criterion(shared=True)
def unnegated_guaranteed_absent(workspace: Path) -> float:
    report = read_report()
    if not report.strip():
        return 0.0
    return score_unnegated_guaranteed_absent(report)


@criterion(shared=True)
def target_slate_coverage(workspace: Path) -> float:
    return score_target_slate_coverage(read_report())


@criterion(shared=True)
def target_scope_date(workspace: Path) -> float:
    report = read_report()
    if not report.strip():
        return 0.0
    scope, _ = cut_before_scoreline_picks_section(report)
    scope = scope[:1000]
    return 1.0 if selected_scope_dates(scope) else 0.0


@criterion(shared=True)
def target_pacific_framing(workspace: Path) -> float:
    report = read_report()
    scope, _ = cut_before_scoreline_picks_section(report)
    return 1.0 if PT_RE.search(scope[:1000]) or PT_RE.search(report[:2000]) else 0.0


@criterion(shared=True)
def target_fixture_mentions(workspace: Path) -> float:
    report = read_report()
    if not report.strip():
        return 0.0
    return score_declared_scored_fixture_coverage(report)


@criterion(shared=True)
def target_slate_scored_coverage(workspace: Path) -> float:
    return score_target_slate_coverage(read_report())


def score_artifact_written(report: str) -> float:
    return 1.0 if report.strip() else 0.0


def score_skill_activation_evidence(atif: bytes | str) -> float:
    return 1.0 if atif_has_skill_activation(atif) else 0.0


def atif_has_skill_activation(data: bytes | str) -> bool:
    try:
        trajectory = json.loads(data)
    except json.JSONDecodeError:
        return False

    for tool_call in iter_atif_tool_calls(trajectory):
        function_name = str(tool_call.get("function_name", "")).lower()
        arguments = tool_call.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}

        if function_name == "read":
            file_path = str(arguments.get("file_path") or arguments.get("path") or "").lower()
            if is_skill_file_path(file_path):
                return True

        if function_name == "exec_command":
            command = str(arguments.get("cmd") or arguments.get("command") or "").lower()
            if command_reads_skill_file(command):
                return True

        if function_name == "skill":
            skill_name = str(
                arguments.get("skill")
                or arguments.get("skill_name")
                or arguments.get("name")
                or arguments.get("path")
                or ""
            ).lower()
            if "world-cup-picks-report" in skill_name:
                return True

    return False


def is_skill_file_path(path: str) -> bool:
    normalized = path.strip().lower()
    return any(
        normalized.endswith(suffix)
        for suffix in (
            "/.agents/skills/world-cup-picks-report/skill.md",
            "/.claude/skills/world-cup-picks-report/skill.md",
        )
    )


def command_reads_skill_file(command: str) -> bool:
    if not any(token in command for token in ("cat ", "sed ", "less ", "head ", "tail ")):
        return False
    return any(
        path in command
        for path in (
            ".agents/skills/world-cup-picks-report/skill.md",
            "/.agents/skills/world-cup-picks-report/skill.md",
            ".claude/skills/world-cup-picks-report/skill.md",
            "/.claude/skills/world-cup-picks-report/skill.md",
        )
    )


def is_oracle_run(config_path: Path | None = None, oracle_log_path: Path | None = None) -> bool:
    config_path = config_path or CONFIG_PATH
    oracle_log_path = oracle_log_path or ORACLE_LOG_PATH

    try:
        config = json.loads(read_text(config_path))
    except json.JSONDecodeError:
        config = {}

    agent = config.get("agent", {})
    if isinstance(agent, dict) and agent.get("name") == "oracle":
        return True

    return oracle_log_path.exists()


def iter_atif_tool_calls(trajectory: object) -> list[dict]:
    if not isinstance(trajectory, dict):
        return []

    tool_calls: list[dict] = []
    for step in trajectory.get("steps", []):
        if not isinstance(step, dict):
            continue
        for tool_call in step.get("tool_calls", []):
            if isinstance(tool_call, dict):
                tool_calls.append(tool_call)
    return tool_calls


def score_citation_proximity(report: str, blocks: list[str]) -> float:
    if not blocks:
        return 0.0
    passed = sum(1 for block in blocks if has_inline_citation(block) or has_centralized_citation(block, report))
    return passed / len(blocks)


def score_scoreline_format(blocks: list[str]) -> float:
    if not blocks:
        return 0.0
    good = 0
    for block in blocks:
        first_line = block.splitlines()[0].strip()
        if VS_LINE_RE.search(first_line) and SCORELINE_RE.search(first_line):
            good += 1
    return good / len(blocks)


def score_guardrails(report: str) -> float:
    if not score_banned_wagering_terms_absent(report):
        return 0.0
    if not score_unnegated_guaranteed_absent(report):
        return 0.0
    return 1.0


def score_banned_wagering_terms_absent(report: str) -> float:
    lower = report.lower()
    for phrase in ("lock of the day", "bankroll", "bet sizing", "stake ", "wager ", "must bet"):
        if phrase in lower:
            return 0.0
    return 1.0


def score_unnegated_guaranteed_absent(report: str) -> float:
    return 0.0 if has_unnegated_guaranteed(report.lower()) else 1.0


def score_target_slate_coverage(
    report: str,
    schedule_path: Path = SCHEDULE_PATH,
    as_of_override: str | None = None,
) -> float:
    if not report.strip():
        return 0.0

    scope, _ = cut_before_scoreline_picks_section(report)
    scope = scope[:1000]

    score = 0.0
    if selected_scope_dates(scope):
        score += 0.25
    if PT_RE.search(scope) or PT_RE.search(report[:2000]):
        score += 0.15

    score += 0.50 * score_declared_scored_fixture_coverage(report)

    if not has_internal_stale_scope_conflict(scope):
        score += 0.10

    return round(score, 4)


def score_declared_scored_fixture_coverage(report: str, expected_minimum: int = 3) -> float:
    if expected_minimum <= 0:
        return 0.0
    fixtures = unique_scored_fixture_lines(match_blocks(report))
    return min(len(fixtures), expected_minimum) / expected_minimum


def unique_scored_fixture_lines(blocks: list[str]) -> set[str]:
    fixtures: set[str] = set()
    for block in blocks:
        first_line = block.splitlines()[0].strip() if block.splitlines() else ""
        fixture_match = VS_LINE_RE.search(first_line)
        if fixture_match and SCORELINE_RE.search(first_line):
            fixtures.add(compact_alnum(fixture_match.group(0)))
    return fixtures


def has_internal_stale_scope_conflict(scope: str) -> bool:
    selected_dates = selected_scope_dates(scope)
    as_of_dates = explicit_as_of_dates(scope)
    if not selected_dates or not as_of_dates:
        return False
    return min(selected_dates) <= max(as_of_dates)


def resolve_target_slate(
    schedule_path: Path = SCHEDULE_PATH,
    as_of_override: str | None = None,
) -> dict:
    schedule = json.loads(schedule_path.read_text())
    as_of_value = as_of_override or os.getenv(AS_OF_DATE_ENV) or schedule["as_of_date_pt"]
    as_of_date = date.fromisoformat(as_of_value)
    earliest_date = as_of_date + timedelta(days=1)

    fixtures_by_date: dict[date, list[dict]] = {}
    for fixture in schedule.get("fixtures", []):
        fixture_date = date.fromisoformat(fixture["date_pt"])
        if fixture_date < earliest_date:
            continue
        fixtures_by_date.setdefault(fixture_date, []).append(fixture)

    if not fixtures_by_date:
        raise ValueError(f"No fixtures found on or after {earliest_date.isoformat()}")

    target_date = min(fixtures_by_date)
    return {
        "as_of_date": as_of_date,
        "earliest_date": earliest_date,
        "date": target_date,
        "fixtures": fixtures_by_date[target_date],
    }


def read_report(path: Path = REPORT_PATH) -> str:
    return read_text(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        return ""


def collect_agent_text(agent_log_dir: Path = AGENT_LOG_DIR, report_path: Path = REPORT_PATH) -> str:
    chunks: list[str] = []
    if agent_log_dir.is_dir():
        for path in sorted(p for p in agent_log_dir.rglob("*") if p.is_file()):
            try:
                if path.stat().st_size <= 5_000_000:
                    chunks.append(read_text(path))
            except OSError:
                continue
    chunks.append(read_text(report_path))
    return "\n".join(chunks).lower()


def commands_from_atif(data: bytes | str) -> list[str]:
    try:
        trajectory = json.loads(data)
    except json.JSONDecodeError:
        return []

    commands: list[str] = []
    for step in trajectory.get("steps", []):
        for tool_call in step.get("tool_calls", []):
            arguments = tool_call.get("arguments", {})
            if not isinstance(arguments, dict):
                continue
            for key in ("command", "cmd"):
                command = arguments.get(key)
                if isinstance(command, str) and command.strip():
                    commands.append(command)
                    break
    return commands


def collect_agent_commands(agent_log_dir: Path = AGENT_LOG_DIR) -> str:
    commands = collect_agent_commands_from_file(agent_log_dir / "trajectory.json")
    if commands:
        return commands
    oracle_path = agent_log_dir / "oracle.txt"
    if not oracle_path.exists():
        return ""
    return collect_agent_shell_trace_commands_from_file(oracle_path)


def collect_agent_commands_from_file(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    return "\n".join(commands_from_atif(data)).lower()


def collect_agent_shell_trace_commands_from_file(path: Path) -> str:
    commands: list[str] = []
    for line in read_text(path).splitlines():
        line = line.strip()
        if line.startswith("+ "):
            command = line[2:].strip()
            if command:
                commands.append(command)
    return "\n".join(commands).lower()


def match_blocks(report: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    in_block = False
    in_scoreline_picks = False

    def flush() -> None:
        nonlocal current
        if current:
            blocks.append("\n".join(current).strip())
        current = []

    for line in report.splitlines():
        trimmed = line.strip()
        if is_scoreline_picks_heading(trimmed):
            if in_block:
                flush()
            in_block = False
            in_scoreline_picks = True
            continue
        if in_scoreline_picks and is_section_heading(trimmed):
            if in_block:
                flush()
            in_block = False
            in_scoreline_picks = False
            continue
        if not in_scoreline_picks:
            continue
        if is_match_pick_line(trimmed):
            if in_block:
                flush()
            in_block = True
            current.append(trimmed)
            continue
        if in_block:
            if is_section_heading(trimmed):
                flush()
                in_block = False
                continue
            current.append(trimmed)

    if in_block:
        flush()
    return blocks


def is_scoreline_picks_heading(line: str) -> bool:
    return normalized_heading(line) == "scoreline picks"


def is_match_pick_line(line: str) -> bool:
    lower = line.lower()
    return (
        (line.startswith("- ") or line.startswith("* ") or line.startswith("### "))
        and " vs " in lower
        and SCORELINE_RE.search(line) is not None
    )


def is_section_heading(line: str) -> bool:
    if not line:
        return False
    return normalized_heading(line) in {
        "best scoreline leans",
        "best leans",
        "traps / upsets to avoid",
        "traps",
        "upsets to avoid",
        "wait for lineups",
        "sources",
        "source",
    }


def normalized_heading(line: str) -> str:
    return line.strip("#:* ").lower()


def has_inline_citation(text: str) -> bool:
    return URL_RE.search(text) is not None


def has_centralized_citation(block: str, report: str) -> bool:
    block = block.lower()
    report = report.lower()
    if has_named_anchor_citation(block, report):
        return True
    if not has_any_term(block, GENERIC_ANCHOR_TERMS):
        return False
    return report_has_source_line(report, GENERIC_ANCHOR_TERMS)


def has_named_anchor_citation(block: str, report: str) -> bool:
    return any(contains_compact(block, anchor) and report_has_source_line(report, (anchor,)) for anchor in ANCHOR_NAMES)


def report_has_source_line(report: str, terms: tuple[str, ...]) -> bool:
    for line in report.splitlines():
        line = line.lower()
        if not has_inline_citation(line):
            continue
        if any(contains_compact(line, term) for term in terms):
            return True
    return False


def has_any_term(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def contains_compact(text: str, term: str) -> bool:
    return compact_alnum(term) in compact_alnum(text)


def compact_alnum(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum() and char.isascii())


def score_report_date_freshness(report: str) -> bool:
    scope, _ = cut_before_scoreline_picks_section(report)
    scope = scope[:800]
    current = datetime.combine(resolve_target_slate()["date"], datetime.min.time())
    matches = DATE_RE.findall(scope)
    if not matches:
        return False
    for match in matches:
        parsed = parse_report_date(match)
        if parsed is not None and parsed < current:
            return False
    return True


def target_date_mentioned(text: str, target_date: date) -> bool:
    target_datetime = datetime.combine(target_date, datetime.min.time())
    accepted = {
        target_datetime.strftime("%A, %B %-d, %Y").lower(),
        target_datetime.strftime("%B %-d, %Y").lower(),
        target_datetime.strftime("%A, %B %d, %Y").lower(),
        target_datetime.strftime("%B %d, %Y").lower(),
        target_date.isoformat(),
    }
    normalized = re.sub(r"\s+", " ", text.lower())
    return any(value in normalized for value in accepted)


def has_scope_date_before(text: str, threshold: date) -> bool:
    for match in DATE_RE.findall(text):
        parsed = parse_report_date(match)
        if parsed is not None and parsed.date() < threshold:
            return True
    return False


def has_selected_scope_date_before(text: str, threshold: date) -> bool:
    for value in selected_scope_dates(text):
        if value < threshold:
            return True
    return False


def selected_scope_dates(text: str) -> list[date]:
    dates: list[date] = []
    for line in text.splitlines():
        if not is_scope_line(line):
            continue
        for match in DATE_RE.finditer(line):
            if has_as_of_date_context(line, match.start()):
                continue
            parsed = parse_report_date(match.group(0))
            if parsed is not None:
                dates.append(parsed.date())

    if dates:
        return dates

    for match in DATE_RE.finditer(text):
        if has_as_of_date_context(text, match.start()):
            continue
        parsed = parse_report_date(match.group(0))
        if parsed is not None:
            dates.append(parsed.date())
    return dates


def explicit_as_of_dates(text: str) -> list[date]:
    dates: list[date] = []
    for match in DATE_RE.finditer(text):
        if not has_as_of_date_context(text, match.start()):
            continue
        parsed = parse_report_date(match.group(0))
        if parsed is not None:
            dates.append(parsed.date())
    return dates


def is_scope_line(line: str) -> bool:
    normalized = line.lower()
    return any(term in normalized for term in ("report scope", "scope:", "slate"))


def has_as_of_date_context(text: str, match_start: int) -> bool:
    prefix = text[max(0, match_start - 100) : match_start].lower()
    return any(
        term in prefix
        for term in (
            "as of",
            "current date",
            "current runtime date",
            "runtime date",
            "from the current",
            "from current",
            "today is",
        )
    )


def fixture_mentioned(report_lower: str, fixture: dict) -> bool:
    home_aliases = team_aliases(str(fixture["home"]))
    away_aliases = team_aliases(str(fixture["away"]))
    compact_report = compact_alnum(report_lower)
    for home in home_aliases:
        for away in away_aliases:
            ordered = compact_alnum(f"{home} vs {away}")
            reverse = compact_alnum(f"{away} vs {home}")
            if ordered in compact_report or reverse in compact_report:
                return True
    return False


def team_aliases(team: str) -> tuple[str, ...]:
    normalized = team.strip().lower()
    return TEAM_ALIASES.get(normalized, (normalized,))


def cut_before_scoreline_picks_section(report: str) -> tuple[str, bool]:
    lines: list[str] = []
    for line in report.splitlines():
        if is_scoreline_picks_heading(line.strip()):
            return "\n".join(lines), True
        lines.append(line)
    return report, False


def parse_report_date(value: str) -> datetime | None:
    for layout in ("%A, %B %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, layout)
        except ValueError:
            continue
    return None


def has_unnegated_guaranteed(text: str) -> bool:
    for match in re.finditer(r"\bguaranteed\b", text):
        start = match.start()
        prefix = text[max(0, start - 20) : start]
        negated = any(term in prefix for term in ("not ", "no ", "never ", "without "))
        if not negated:
            sentence_start = max(text.rfind(mark, 0, start) for mark in ".!?;\n")
            sentence_start = 0 if sentence_start < 0 else sentence_start
            sentence_prefix = text[sentence_start:start]
            negated = any(term in sentence_prefix for term in ("don't ", "do not ", "avoid ", "not "))
        if not negated:
            return True
    return False
