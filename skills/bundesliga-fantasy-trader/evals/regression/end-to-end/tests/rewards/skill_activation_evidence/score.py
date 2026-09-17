"""Check that the injected Bundesliga Fantasy skill was activated."""

from rewardkit import criteria


criteria.skill_activation_evidence(weight=1.0, name="bundesliga_skill_activation_detected")
