---
cwd: ../../../../..
---

# Bundesliga Fantasy Trader end-to-end eval

This task freezes Bundesliga Fantasy 2026/27 Matchday 4 at September 17,
2026, 8:48 a.m. America/Los_Angeles. The agent works only from the staged
pre-deadline snapshot, the verifier rejects external retrieval in the agent
trajectory, and the agent writes `/logs/artifacts/report.md`.

The verifier uses deterministic checks only for the artifact and observable
trajectory behavior: injected-skill activation and the offline evidence
boundary. Temporal integrity, task-contract fulfillment, budget and state
safety, decision quality, and evidence quality are graded semantically so
equivalent natural-language reports do not depend on exact phrases or
headings.

From the repository root, run the reference oracle:

```sh
visr run skills/bundesliga-fantasy-trader/evals/regression --task-dir end-to-end
```

Run it with Codex:

```sh
visr run skills/bundesliga-fantasy-trader/evals/regression --task-dir end-to-end --agent codex --ak reasoning_effort=xhigh
```

`visr` supplies the downstream model access used by the semantic judges. Run
the deterministic unit tests without launching an agent:

```sh
uvx --from harbor-rewardkit --with pytest pytest -q \
  skills/bundesliga-fantasy-trader/evals/regression/end-to-end/tests/unit
```
