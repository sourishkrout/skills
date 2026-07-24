# Sebastian's Benchmarked Skills

Reusable AI agent skills, each with a regression eval track record. That track
record is the main artifact, so start there before cloning or running anything.

## Review the evals

The 2026 World Cup has wrapped, but the eval track record lives on and is still
worth a look.

| Dashboard | Best for |
| --- | --- |
| [**Trend dashboard →**](https://bench.visr.dev/repo/github.com/sourishkrout/skills/skills-world-cup-picks-report-evals-regression/trials) | Top-line metrics and regression trends over time |
| [**Harbor dashboard →**](https://world-cup-picks-report-evals.sourishkrout.workers.dev) | The complete historical record of every job and task trial |

Or browse the same history locally after cloning:

```sh {"background":"true","name":"history"}
runme eval view
```

## Use a skill

Install `world-cup-picks-report` globally from this repo:

```sh
npx skills add -g https://github.com/sourishkrout/skills --skill world-cup-picks-report
```

Or add it through the Claude Code marketplace:

```text
/plugin marketplace add sourishkrout/skills
/plugin install world-cup-picks-report@sourishkrout-skills
```

---

## Contributing

Everything below is for running, promoting, and deploying the evals locally.

Runme's eval workflow is documented at <https://docs.runme.dev/eval/>.

Current skill:

- `world-cup-picks-report` in `skills/world-cup-picks-report`

### Run the evals

The regression verifier uses Anthropic-backed LLM judges. Export an Anthropic
API key before running the evals:

```sh
export ANTHROPIC_API_KEY=...
```

Run the full regression eval from the repo root:

```sh {"name":"eval","terminalRows":"34"}
runme eval skills/world-cup-picks-report/evals/regression \
    --agent codex \
    --ak reasoning_effort=xhigh
```

To run only the oracle:

```sh {"name":"oracle","terminalRows":"34"}
runme eval skills/world-cup-picks-report/evals/regression
```

You can substitute another supported agent, such as `cursor-cli`, `claude-code`,
or `openclaw`, for `codex`.

### Promote fresh results

After running an eval, compare the latest local job against the latest
Git-tracked baseline:

```sh
runme eval compare skills/world-cup-picks-report/evals/regression
```

Preview the promotion before committing evidence:

```sh
runme eval promote skills/world-cup-picks-report/evals/regression --latest --dry-run
```

If the result should become the new baseline, stage the related source changes
and promote the eval evidence:

```sh
git add <changed-files>
runme eval promote skills/world-cup-picks-report/evals/regression --latest
```

Promotion records compact eval evidence by default. Use `--artifacts` only when
you need full logs and trial outputs; artifacts can contain sensitive
information. Use `--evidence-only` when promoting eval evidence without source
changes.

Review artifacts before promoting, because the Harbor showcase is public. Push
the promotion commit to `main` and GitHub Actions publishes the fresh results.
