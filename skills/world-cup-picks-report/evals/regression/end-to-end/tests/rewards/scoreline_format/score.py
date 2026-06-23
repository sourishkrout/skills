"""Check that match picks include explicit home:away scorelines."""

import rewardkit as rk
from rewardkit import criteria


rk.command_succeeds(
    "grep -Eiq '^#{0,6}[[:space:]]*Scoreline Picks[[:space:]]*$|^Scoreline Picks[[:space:]]*$' /logs/artifacts/report.md",
    weight=1.0,
    name="scoreline_picks_section_present",
)
rk.command_succeeds(
    "grep -Eq '[0-9]+[[:space:]]*:[[:space:]]*[0-9]+' /logs/artifacts/report.md",
    weight=1.0,
    name="scoreline_pattern_present",
)
criteria.parsed_scoreline_format(
    weight=3.0,
    name="match_pick_headings_include_scorelines",
)
