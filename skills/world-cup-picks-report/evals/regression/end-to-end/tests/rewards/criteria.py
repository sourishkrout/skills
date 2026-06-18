from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from rewardkit import criterion


AGENT_LOG_DIR = Path("/logs/agent")
ARTIFACTS_DIR = Path("/logs/artifacts")
CONFIG_PATH = Path("/logs/config.json")
ORACLE_LOG_PATH = AGENT_LOG_DIR / "oracle.txt"
REPORT_PATH = ARTIFACTS_DIR / "report.md"
EXPECTED_REPORT_DATE = "2026-06-27"

SCORELINE_RE = re.compile(r"\b\d+\s*:\s*\d+\b")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
VS_LINE_RE = re.compile(r"\b[0-9A-Za-z][^:\n]{1,100}\s+vs\.?\s+[^:\n]{1,100}", re.I)
DATE_RE = re.compile(
    r"\b(?:(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday),\s*)?"
    r"(?:january|february|march|april|may|june|july|august|september|october|"
    r"november|december)\s+\d{1,2},\s+2026\b",
    re.I,
)

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
def scoreline_format(workspace: Path) -> float:
    return score_scoreline_format(match_blocks(read_report()))


@criterion(shared=True)
def guardrails(workspace: Path) -> float:
    return score_guardrails(read_report())


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
    lower = report.lower()
    for phrase in ("lock of the day", "bankroll", "bet sizing", "stake ", "wager ", "must bet"):
        if phrase in lower:
            return 0.0
    if has_unnegated_guaranteed(lower):
        return 0.0
    return 1.0


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
    current = datetime.strptime(EXPECTED_REPORT_DATE, "%Y-%m-%d")
    matches = DATE_RE.findall(scope)
    if not matches:
        return False
    for match in matches:
        parsed = parse_report_date(match)
        if parsed is not None and parsed < current:
            return False
    return True


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
