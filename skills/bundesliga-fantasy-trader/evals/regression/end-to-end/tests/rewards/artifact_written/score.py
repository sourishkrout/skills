"""Check that the requested report artifact exists and is non-empty."""

from rewardkit import criteria


criteria.artifact_written(weight=1.0, name="report_artifact_written")
