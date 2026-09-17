from __future__ import annotations

import json
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


@criterion(shared=True)
def artifact_written(workspace: Path) -> float:
    return score_artifact_written(read_report())


@criterion(shared=True)
def skill_activation_evidence(workspace: Path) -> float:
    trajectory = read_text(AGENT_LOG_DIR / "trajectory.json")
    if trajectory:
        return score_skill_activation_evidence(trajectory)
    return 1.0 if is_oracle_run() else 0.0


def score_artifact_written(report: str) -> float:
    return 1.0 if report.strip() else 0.0


def score_skill_activation_evidence(data: bytes | str) -> float:
    try:
        trajectory = json.loads(data)
    except (json.JSONDecodeError, TypeError):
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
