"""Reject obvious hindsight and post-cutoff leakage."""

from rewardkit import criteria


criteria.temporal_integrity(weight=1.0, name="frozen_cutoff_respected")
