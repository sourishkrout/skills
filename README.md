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

## Public eval showcase

Eval history is published at:

```text
https://world-cup-picks-report.evals.visr.dev
```

The showcase is served by a Cloudflare Worker Container running Harbor against
the committed `.runme/evals/jobs` snapshot. To publish fresh results, commit the
updated eval jobs and push to `main`; GitHub Actions deploys the new container
with Wrangler.

Local Docker smoke test:

```sh
docker build -f Dockerfile.eval-viewer -t skills-eval-viewer .
docker run --rm -p 8080:8080 skills-eval-viewer
```

Manual Cloudflare deploy:

```sh
npm install
npm run check
npm run deploy
```

The deployment is intentionally public, so review artifacts before committing
eval results.
