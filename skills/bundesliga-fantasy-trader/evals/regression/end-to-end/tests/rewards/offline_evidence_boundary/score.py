"""Check that the agent stayed within the staged offline evidence set."""

from rewardkit import criteria


criteria.offline_evidence_boundary(weight=1.0, name="no_external_network_use")
