"""Check that lineup guidance is actionable rather than a generic wait caveat."""

from rewardkit import criteria


criteria.lineup_status_actionable(
    weight=1.0,
    name="lineup_status_confirmed_or_materially_pending",
)
