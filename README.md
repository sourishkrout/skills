# Sourishkrout Skills

This repo contains reusable AI agent skills and their regression evals. The main
artifact is the eval history for each skill, so start there before cloning or
running anything locally.

## Review eval history

Published eval history:

<https://world-cup-picks-report-evals.sourishkrout.workers.dev>

Local history viewer:

```sh {"background":"true","name":"history"}
runme eval view
```

The public showcase is deployed from promoted eval jobs. Review artifacts before
promoting results because the deployment is intentionally public.

## Run the evals

Current skill:

- `world-cup-picks-report` in `skills/world-cup-picks-report`

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

## Install a skill

Install `world-cup-picks-report` globally from this repo:

```sh
npx skills add -g https://github.com/sourishkrout/skills --skill world-cup-picks-report
```

## Install as a plugin

Claude Code marketplace:

```text
/plugin marketplace add sourishkrout/skills
/plugin install world-cup-picks-report@sourishkrout-skills
```

Codex repo marketplace metadata lives at `.agents/plugins/marketplace.json`.
Codex can read that catalog when this repository is used as a marketplace
source. The marketplace metadata highlights that the packaged skills are
maintained with Harbor-backed regression evals, with public eval history linked
above.

## Promote fresh results

Runme's eval workflow is documented at:

```text
https://docs.runme.dev/eval/
```

After running an eval, compare the latest local job against the latest
Git-tracked baseline:

```sh
runme eval compare
```

Preview the promotion before committing evidence:

```sh
runme eval promote --latest --dry-run
```

If the result should become the new baseline, stage the related source changes
and promote the eval evidence:

```sh
git add <changed-files>
runme eval promote --latest
```

Promotion records compact eval evidence by default. Use `--artifacts` only when
you need full logs and trial outputs; artifacts can contain sensitive
information. Use `--evidence-only` when promoting eval evidence without source
changes.

## Deploy the showcase

The showcase is served by a Cloudflare Worker Container running Harbor against
the promoted eval jobs. Push the promotion commit to `main` to publish fresh
results.

GitHub Actions deploys the new container with Wrangler.

## Viewer development

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
