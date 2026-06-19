# Skills

- `world-cup-picks-report` in `skills/world-cup-picks-report`

Run evals from the skill root:

```sh {"name":"eval"}
runme eval skills/world-cup-picks-report/evals/regression \
    --agent openclaw \
    --ak reasoning_effort=xhigh
```

Or, substitute `openclaw` with `claude-code` or `codex`.

## History

Review each skill's latest eval results:

```sh {"background":"true","name":"history"}
uvx harbor view .runme/evals/jobs
```
