# Skills

- `world-cup-picks-report` in `skills/world-cup-picks-report`

Run evals from the skill root:

```sh {"name":"eval","terminalRows":"34"}
runme eval skills/world-cup-picks-report/evals/regression \
    --agent codex \
    --ak reasoning_effort=xhigh
```

Or, substitute `cursor-cli` with `claude-code` or `codex`.

To only run the oracle, please use:

```sh {"name":"oracle","terminalRows":"34"}
runme eval skills/world-cup-picks-report/evals/regression
```

## History

Review each skill's latest eval results:

```sh {"background":"true","name":"history"}
runme eval view
```
