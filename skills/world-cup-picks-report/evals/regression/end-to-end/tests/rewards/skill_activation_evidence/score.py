"""Check that the agent activated or followed the world-cup-picks-report skill."""

import rewardkit as rk
from rewardkit import criteria


rk.command_succeeds(
    "test -s /logs/agent/trajectory.json || test -s /logs/agent/oracle.txt",
    weight=0.0,
    name="activation_log_present",
)
rk.trajectory_tool_used(
    "Read",
    path="/logs/agent/trajectory.json",
    weight=0.0,
    name="read_tool_used",
)
rk.trajectory_tool_used(
    "Skill",
    path="/logs/agent/trajectory.json",
    weight=0.0,
    name="skill_tool_used",
)
criteria.skill_activation_evidence(
    weight=1.0,
    name="world_cup_skill_activation_detected",
)
