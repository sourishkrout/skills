"""Check that the report avoids wagering certainty and bet-sizing advice."""

from rewardkit import criteria


criteria.guardrails(weight=1.0)
