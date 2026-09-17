FROM ubuntu:24.04

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl python3 \
  && rm -rf /var/lib/apt/lists/* \
  && curl -LsSf https://astral.sh/uv/install.sh | sh \
  && ln -s /root/.local/bin/uv /usr/local/bin/uv \
  && ln -s /root/.local/bin/uvx /usr/local/bin/uvx

COPY workdir /app/skills/bundesliga-fantasy-trader/evals/regression/end-to-end/workdir

RUN test -s /app/skills/bundesliga-fantasy-trader/evals/regression/end-to-end/workdir/.agents/skills/bundesliga-fantasy-trader/SKILL.md \
  && test -s /app/skills/bundesliga-fantasy-trader/evals/regression/end-to-end/workdir/.agents/skills/bundesliga-fantasy-trader/references/rules-2026-27.md \
  && test -s /app/skills/bundesliga-fantasy-trader/evals/regression/end-to-end/workdir/.claude/skills/bundesliga-fantasy-trader/SKILL.md \
  && test -s /app/skills/bundesliga-fantasy-trader/evals/regression/end-to-end/workdir/.claude/skills/bundesliga-fantasy-trader/references/rules-2026-27.md

WORKDIR /app/skills/bundesliga-fantasy-trader/evals/regression/end-to-end/workdir
