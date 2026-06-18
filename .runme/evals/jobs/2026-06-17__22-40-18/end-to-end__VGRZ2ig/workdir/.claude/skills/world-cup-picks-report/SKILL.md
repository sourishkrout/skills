---
name: "world-cup-picks-report"
description: "Generate World Cup scoreline reports using expert picks, model, market, and Elo checks."
---

# World Cup Picks Report

Use this skill when Sebastian asks for World Cup predictions, picks, scorelines, results, a matchday report, or to run the current/next round picking process.

## Purpose

Produce a concise, practical picks report that blends expert score predictions, model probabilities, betting-market consensus, team-strength ratings, and current match context. The goal is better pool/bracket score picks, not gambling advice.

## Required Output

Every match must include a predicted final score/result in `home:away` format, for example `1:3`. If the fixture is listed as `Team A vs Team B`, the score must be in that same order.

## Inputs

- `date`: Today's date in the user/runtime timezone. Use the actual current date and timezone from the runtime context.
- `round_scope`: If the user does not specify a round, choose the current round if matches are being played today; otherwise choose the next scheduled round/matchday.
- `competition`: FIFA World Cup unless the user specifies another tournament.

## Source Priority

1. Official FIFA fixtures/schedule for match list and dates.
2. Expert correct-score predictions from reputable preview or betting-analysis sources.
3. Opta Analyst / Opta Supercomputer for match probabilities and model framing.
4. Sportsbook consensus or odds comparison, such as Oddschecker, for market-implied expectations.
5. World Football Elo Ratings for team-strength sanity checks.
6. One current match preview or team-news source per match when available.

## Workflow

1. Identify the target matches.
   - Search for today's World Cup fixtures.
   - Convert kickoff times into the user/runtime timezone before deciding whether a fixture belongs to today.
   - Include cross-midnight fixtures when they fall on the user/runtime date, even if a source lists them under the next calendar day in ET, UTC, or local venue time.
   - If there are no matches today, find the next scheduled matchday or next round.
   - Use absolute dates and name the timezone in the report.

2. Collect expert scoreline anchors.
   - Search each fixture with terms like `prediction correct score`, `expert pick`, `score prediction`, and `odds`.
   - Prefer sources that explicitly publish a scoreline or correct-score lean.
   - If multiple expert scorelines exist, choose the one most consistent with the market/model and note disagreement briefly.

3. Collect baseline probabilities.
   - Prefer Opta match probabilities when available.
   - If Opta is missing, use odds-implied probability as the baseline and say so.

4. Cross-check the betting market.
   - Compare the scoreline/winner pick with sportsbook consensus.
   - Flag any mismatch where the expert pick and market disagree.

5. Sanity-check team strength.
   - Use World Football Elo or comparable ratings.
   - Note if a famous team appears weaker/stronger than reputation suggests.

6. Add current-context checks.
   - Look for injuries, likely rotation, suspensions, weather/travel, and motivation.
   - Keep this short and avoid overfitting to narrative.

7. Make the scoreline pick.
   - For each match provide: exact score, confidence, expert/model basis, and risk note.
   - Confidence levels: High, Medium, Low.
   - In group stages, be conservative and respect draws.
   - Common conservative patterns: favorite `2:0` or `2:1`, close favorite `1:0`, draw-risk game `1:1`, heavy favorite `3:0` only when market/model strongly support it.

8. End with an action summary.
   - Best scoreline picks.
   - Traps/upsets to avoid.
   - Matches where the user should wait for lineups.

## Report Format

Keep Discord output concise. Avoid markdown tables. Use markdown headings to make the report scannable: `##` for report sections and `###` for each game pick. In `Scoreline Picks`, write each game as a short paragraph entry with the pick in the heading. Put `Basis:` and `Risk:` on their own lines below the pick.

Recommended structure:

- Scope line: `Report scope: [round/matchday], [absolute date range]`
- Timezone-aware scope example: `Report scope: [round/matchday], Saturday, June 27, 2026 in U.S. Pacific time`
- `## Scoreline Picks`
  `### Team A vs Team B: 2:1 - Confidence: Medium`
  `Basis: expert pick/model/market summary`
  `Risk: ...`
- `## Best Scoreline Leans`
- `## Traps / Upsets To Avoid`
- `## Wait For Lineups`
- `## Sources`

## Guardrails

- Always browse/search current sources before making picks.
- Include links to sources used.
- Do not present scorelines as guaranteed outcomes.
- Do not encourage wagering or bankroll decisions unless explicitly asked; even then, keep it informational.
- If expert scoreline data is thin or conflicting, say so and lower confidence.
