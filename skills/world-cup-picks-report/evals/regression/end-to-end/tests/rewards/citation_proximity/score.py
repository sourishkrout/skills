"""Check that match picks are traceable to nearby or centralized citations."""

import rewardkit as rk
from rewardkit import criteria


rk.command_succeeds(
    "grep -Eq 'https?://' /logs/artifacts/report.md",
    weight=0.0,
    name="report_has_url",
)
rk.command_succeeds(
    "grep -Eiq 'opta|dimers|football whispers|espn|elo|prediction|preview|correct.score' /logs/artifacts/report.md",
    weight=0.0,
    name="report_has_source_terms",
)
criteria.citation_proximity_by_match(
    weight=1.0,
    name="match_blocks_have_traceable_citations",
)
