"""Check that the report declares and covers a coherent World Cup slate."""

from rewardkit import criteria


criteria.target_scope_date(
    weight=0.0,
    name="target_scope_date_present",
)
criteria.target_pacific_framing(
    weight=0.25,
    name="target_pacific_framing_present",
)
criteria.target_fixture_mentions(
    weight=0.0,
    name="target_fixture_mentions",
)
criteria.target_slate_scored_coverage(
    weight=1.0,
    name="target_slate_weighted_coverage",
)
