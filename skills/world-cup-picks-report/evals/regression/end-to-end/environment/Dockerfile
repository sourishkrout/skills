FROM ubuntu:24.04

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl python3 \
  && rm -rf /var/lib/apt/lists/* \
  && curl -LsSf https://astral.sh/uv/install.sh | sh \
  && ln -s /root/.local/bin/uv /usr/local/bin/uv \
  && ln -s /root/.local/bin/uvx /usr/local/bin/uvx

COPY workdir /app/skills/world-cup-picks-report/evals/regression/end-to-end/workdir

RUN test -s /app/skills/world-cup-picks-report/evals/regression/end-to-end/workdir/.agents/skills/world-cup-picks-report/SKILL.md \
  && test -s /app/skills/world-cup-picks-report/evals/regression/end-to-end/workdir/.claude/skills/world-cup-picks-report/SKILL.md

WORKDIR /app/skills/world-cup-picks-report/evals/regression/end-to-end/workdir
