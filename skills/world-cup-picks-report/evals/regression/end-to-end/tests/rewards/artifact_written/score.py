"""Check that the final report artifact was written."""

import rewardkit as rk


rk.command_succeeds(
    "test -f /logs/artifacts/report.md",
    weight=1.0,
    name="report_file_exists",
)
rk.command_succeeds(
    "test -s /logs/artifacts/report.md",
    weight=2.0,
    name="report_file_nonempty",
)
