from __future__ import annotations

import json
import re
from pathlib import Path

from rewardkit import criterion


AGENT_LOG_DIR = Path("/logs/agent")
ARTIFACTS_DIR = Path("/logs/artifacts")
CONFIG_PATH = Path("/logs/config.json")
REPORT_PATH = ARTIFACTS_DIR / "report.md"
INJECTED_SKILL_PATHS = (
    ".agents/skills/bundesliga-fantasy-trader/skill.md",
    "/.agents/skills/bundesliga-fantasy-trader/skill.md",
    ".claude/skills/bundesliga-fantasy-trader/skill.md",
    "/.claude/skills/bundesliga-fantasy-trader/skill.md",
)
READ_COMMANDS = ("cat ", "sed ", "less ", "head ", "tail ")
SHELL_TOOL_NAMES = {"exec_command", "bash", "shell"}
WRAPPED_NETWORK_TOOL_RE = re.compile(
    r"\btools\.[a-z0-9_]*(?:web|search|browser|http|fetch|open_url)[a-z0-9_]*\s*\(",
    re.I,
)
SHELL_NETWORK_RE = re.compile(r"(?:^|[;&|(\s\"'])(?:curl|wget)\s", re.I)


@criterion(shared=True)
def artifact_written(workspace: Path) -> float:
    return score_artifact_written(read_report())


@criterion(shared=True)
def skill_activation_evidence(workspace: Path) -> float:
    trajectory = read_text(AGENT_LOG_DIR / "trajectory.json")
    if trajectory:
        return score_skill_activation_evidence(trajectory)
    return 1.0 if is_oracle_run() else 0.0


@criterion(shared=True)
def temporal_integrity(workspace: Path) -> float:
    report_score = score_temporal_integrity(read_report())
    trajectory = read_text(AGENT_LOG_DIR / "trajectory.json")
    if not trajectory and is_oracle_run():
        return report_score
    return min(report_score, score_no_external_network_use(trajectory))


@criterion(shared=True)
def task_contract(workspace: Path) -> float:
    return score_task_contract(read_report())


@criterion(shared=True)
def budget_and_state_safety(workspace: Path) -> float:
    return score_budget_and_state_safety(read_report())


def score_artifact_written(report: str) -> float:
    return 1.0 if report.strip() else 0.0


def score_skill_activation_evidence(data: bytes | str) -> float:
    try:
        trajectory = json.loads(data)
    except json.JSONDecodeError:
        return 0.0

    for call in iter_tool_calls(trajectory):
        name = str(call.get("function_name", "")).lower()
        arguments = call.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}

        if name == "skill" and skill_tool_names_bundesliga_skill(arguments):
            return 1.0
        if name == "read" and is_injected_skill_path(
            str(arguments.get("file_path") or arguments.get("path") or "")
        ):
            return 1.0
        if name in SHELL_TOOL_NAMES and command_reads_injected_skill(
            direct_command(arguments)
        ):
            return 1.0
        if name == "exec" and wrapped_exec_reads_injected_skill(
            str(arguments.get("input") or "")
        ):
            return 1.0
    return 0.0


def skill_tool_names_bundesliga_skill(arguments: dict) -> bool:
    skill_name = str(
        arguments.get("skill")
        or arguments.get("skill_name")
        or arguments.get("name")
        or arguments.get("path")
        or ""
    ).lower()
    return "bundesliga-fantasy-trader" in skill_name


def is_injected_skill_path(path: str) -> bool:
    normalized = path.strip().lower()
    return any(normalized.endswith(suffix) for suffix in INJECTED_SKILL_PATHS)


def command_reads_injected_skill(command: str) -> bool:
    normalized = command.lower()
    return any(token in normalized for token in READ_COMMANDS) and any(
        path in normalized for path in INJECTED_SKILL_PATHS
    )


def wrapped_exec_reads_injected_skill(source: str) -> bool:
    normalized = source.lower()
    return "tools.exec_command" in normalized and command_reads_injected_skill(normalized)


def direct_command(arguments: dict) -> str:
    return str(arguments.get("cmd") or arguments.get("command") or "")


def iter_tool_calls(trajectory: object) -> list[dict]:
    if not isinstance(trajectory, dict):
        return []
    calls: list[dict] = []
    for step in trajectory.get("steps", []):
        if isinstance(step, dict):
            calls.extend(call for call in step.get("tool_calls", []) if isinstance(call, dict))
    return calls


def score_no_external_network_use(data: bytes | str) -> float:
    try:
        trajectory = json.loads(data)
    except json.JSONDecodeError:
        return 0.0

    network_tool_terms = ("web", "search", "browser", "http", "fetch", "open_url")
    for call in iter_tool_calls(trajectory):
        name = str(call.get("function_name", "")).lower()
        arguments = call.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}
        if any(term in name for term in network_tool_terms):
            return 0.0
        if name in SHELL_TOOL_NAMES and SHELL_NETWORK_RE.search(direct_command(arguments)):
            return 0.0
        if name == "exec":
            source = str(arguments.get("input") or "")
            if WRAPPED_NETWORK_TOOL_RE.search(source):
                return 0.0
            if "tools.exec_command" in source.lower() and SHELL_NETWORK_RE.search(source):
                return 0.0
    return 1.0


def score_temporal_integrity(report: str) -> float:
    if not report.strip():
        return 0.0
    lower = report.lower()
    checks = [
        "september 17, 2026" in lower and "8:48" in lower,
        any(term in lower for term in ("upcoming", "unplayed", "future-facing", "treated as upcoming")),
        not any(
            term in lower
            for term in (
                "matchday 4 result",
                "after matchday 4",
                "matchday 4 ended",
                "final score",
                "in hindsight",
                "as we now know",
                "went on to",
                "eventual outcome",
            )
        ),
        not has_unexpected_scoreline(report),
        not has_post_cutoff_source_date(report),
    ]
    return round(sum(checks) / len(checks), 4)


def has_unexpected_scoreline(report: str) -> bool:
    scrubbed = report
    for allowed_time in ("20:30", "18:30", "11:30", "8:48", "15:48", "17:48"):
        scrubbed = scrubbed.replace(allowed_time, "")
    return bool(re.search(r"\b\d+\s*:\s*\d+\b", scrubbed))


def has_post_cutoff_source_date(report: str) -> bool:
    post_cutoff = re.compile(
        r"\b(?:september\s+(?:1[89]|2\d|30)|october|november|december)"
        r"(?:\s+\d{1,2})?,?\s+2026\b",
        re.I,
    )
    for line in report.splitlines():
        lower = line.lower()
        if any(term in lower for term in ("source", "published", "updated", "viewed", "model data")):
            if post_cutoff.search(line):
                return True
    return False


def score_task_contract(report: str) -> float:
    if not report.strip():
        return 0.0
    lower = report.lower()
    fallback_count = len(re.findall(r"^#{1,6}\s+fallback package\s*$", report, re.I | re.M))
    checks = [
        "what to do now" in lower,
        "recommended package" in lower,
        fallback_count == 1,
        "trigger" in lower,
        "proposed" in lower and ("→" in report or "->" in report),
        all(token in lower for token in ("20:30 cest", "18:30 utc", "11:30")),
        bool(re.search(r"\b[3-5]-[3-5]-[1-3]\b", report)) and "bench" in lower,
        all(term in lower for term in ("def", "mid", "for")) and ("★" in report or "star" in lower),
    ]
    return round(sum(checks) / len(checks), 4)


def score_budget_and_state_safety(report: str) -> float:
    if not report.strip():
        return 0.0
    lower = report.lower()
    checks = [
        "3.34m" in lower,
        "155.13m" in lower and any(term in lower for term in ("not treated as bank", "not spendable", "not available budget")),
        "unknown" in lower and "estimated" in lower,
        any(term in lower for term in ("threshold", "feasible when", "budget condition")),
        all(term in report for term in ("+", "-", "=")),
        "0/5" in lower or bool(re.search(r"uses?\s+\d+\s+of\s+5", lower)),
        all(term in lower for term in ("2 gk", "def", "mid", "for")) and "three" in lower,
        not claims_completed_transfer(report),
    ]
    return round(sum(checks) / len(checks), 4)


def claims_completed_transfer(report: str) -> bool:
    for line in report.splitlines():
        lower = line.lower()
        if not any(term in lower for term in ("completed", "executed")):
            continue
        if any(term in lower for term in ("no transfer", "not completed", "not executed", "has not", "have not", "remain proposed")):
            continue
        if any(term in lower for term in ("transfer", "move", "package")):
            return True
    return False


def is_oracle_run() -> bool:
    try:
        config = json.loads(read_text(CONFIG_PATH))
    except json.JSONDecodeError:
        config = {}
    agent = config.get("agent", {})
    if isinstance(agent, dict) and agent.get("name") == "oracle":
        return True
    return (AGENT_LOG_DIR / "oracle.txt").exists()


def read_report() -> str:
    return read_text(REPORT_PATH)


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        return ""
