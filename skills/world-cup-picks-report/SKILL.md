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

For knockout-stage matches, every match must also include:

- `90-min score`: the score after regulation time.
- `AET/PK outcome`: the expected after-extra-time result, or the penalty shootout result if the match is projected to reach penalties.
- `PK likelihood`: Low, Medium, or High, with a short reason.
- `Aggregate incl. PKs`: a separate pool/bracket-style aggregate that adds made shootout penalties to the match goals, for example `Official: 1:1 AET; PKs: 4:3; Aggregate incl. PKs: 5:4`.

Do not blend penalty shootout goals into the official match score. Keep the official score and the aggregate-including-PKs score visibly separate.

## Inputs

- `date`: Today's date in the user/runtime timezone. Use the actual current date and timezone from the runtime context.
- `round_scope`: If the user does not specify a round, choose the current round if matches are being played today; otherwise choose the next scheduled round/matchday.
- `competition`: FIFA World Cup unless the user specifies another tournament.

## Source Priority

1. Official FIFA fixtures/schedule for match list and dates.
2. Expert correct-score predictions from reputable preview or betting-analysis sources.
3. Opta Analyst / Opta Supercomputer for match probabilities and model framing.
4. Sportsbook consensus or odds comparison, such as Oddschecker, for market-implied expectations.
5. Knockout-specific market signals when available: draw-after-90 odds, extra-time odds, team-to-advance odds, and win-on-penalties odds.
6. World Football Elo Ratings for team-strength sanity checks.
7. Confirmed starting lineups when matches are close to kickoff: FIFA match centres or official match pages first, then ESPN/FotMob/SofaScore or comparable live match centres, then official federation/team channels.
8. One current match preview or team-news source per match when confirmed lineups are not yet available.

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

5. For knockout-stage matches, assess extra-time and penalty risk.
   - Use draw-after-90 probability as the main signal for whether the match can reach extra time.
   - Use team-to-advance, win-on-penalties, and draw/under market context when available to estimate shootout likelihood.
   - Treat closely matched teams, low totals, defensive styles, and conservative tactical incentives as higher PK-risk factors.
   - Treat a clear favorite with strong regulation-win support as lower PK risk even if the under is popular.
   - If explicit PK markets are missing, say the PK assessment is inferred from draw-after-90, total-goals, model, and team-strength signals.

6. Sanity-check team strength.
   - Use World Football Elo or comparable ratings.
   - Note if a famous team appears weaker/stronger than reputation suggests.

7. Add current-context checks.
   - Look for injuries, likely rotation, suspensions, weather/travel, and motivation.
   - For fixtures within 90 minutes of kickoff, explicitly search for confirmed starting lineups.
   - If confirmed lineups are available, use them in the pick and state the material impact, even if the impact is "no change."
   - If confirmed lineups are unavailable, say lineups are pending only when the unresolved starter, formation, or availability question materially affects the scoreline or confidence.
   - For fixtures more than 90 minutes away, use injuries and projected lineups normally, but avoid blanket "wait for lineups" language unless there is a concrete unresolved starter or tactical role.
   - Keep this short and avoid overfitting to narrative.

8. Make the scoreline pick.
   - For each match provide: exact score, confidence, expert/model basis, and risk note.
   - Confidence levels: High, Medium, Low.
   - In group stages, be conservative and respect draws.
   - In knockout stages, distinguish the regulation pick from the advancement pick.
   - If the match is picked to go to penalties, provide the official AET score, projected PK shootout score, advancing team, and aggregate including PKs.
   - If the match is not picked to go to penalties, still include a PK likelihood line and whether the aggregate including PKs is unchanged.
   - Common conservative patterns: favorite `2:0` or `2:1`, close favorite `1:0`, draw-risk game `1:1`, heavy favorite `3:0` only when market/model strongly support it.

9. End with an action summary.
   - Best scoreline picks.
   - Highest PK-risk matches.
   - Traps/upsets to avoid.
   - Lineup status: confirmed lineups incorporated, or specific material lineup questions still pending.

## Report Format

Keep Discord output concise. Avoid markdown tables. Use markdown headings to make the report scannable: `##` for report sections and `###` for each game pick. In `Scoreline Picks`, write each game as a short paragraph entry with the pick in the heading. Put `Basis:` and `Risk:` on their own lines below the pick.

Recommended structure:

- Scope line: `Report scope: [round/matchday], [absolute date range]`
- Timezone-aware scope example: `Report scope: [round/matchday], Saturday, June 27, 2026 in U.S. Pacific time`
- `## Scoreline Picks`
  `### Team A vs Team B: 2:1 - Confidence: Medium`
  `Basis: expert pick/model/market summary`
  `Risk: ...`
- Knockout-stage heading example without PKs:
  `### Team A vs Team B: 2:1 - Aggregate incl. PKs: 2:1 - Confidence: Medium`
  `90-min score: Team A 2:1 Team B`
  `AET/PK outcome: Team A advances in regulation; no PK aggregate adjustment`
  `PK likelihood: Low - market/model favor a regulation winner`
  `Basis: expert pick/model/market summary`
  `Risk: ...`
- Knockout-stage heading example with PKs:
  `### Team A vs Team B: 1:1 AET, Team A advance 4:3 on PKs - Aggregate incl. PKs: 5:4 - Confidence: Low`
  `90-min score: Team A 1:1 Team B`
  `AET/PK outcome: 1:1 AET; Team A win PKs 4:3`
  `PK likelihood: High - draw-after-90 and low-total signals are elevated`
  `Basis: expert pick/model/market summary`
  `Risk: ...`
- `## Best Scoreline Leans`
- `## Highest PK-Risk Matches` for knockout-stage reports
- `## Traps / Upsets To Avoid`
- `## Lineup Status`
- `## Sources`

Lineup status examples:

- Confirmed: `Lineups checked: Norway start Haaland, Odegaard, and Sorloth; no change to 2:1 Norway.`
- Pending: `Lineups pending: wait on Mexico striker/keeper because it affects 1:1 vs 2:1.`

## Guardrails

- Always browse/search current sources before making picks.
- Include links to sources used.
- Do not present scorelines as guaranteed outcomes.
- Do not encourage wagering or bankroll decisions unless explicitly asked; even then, keep it informational.
- If expert scoreline data is thin or conflicting, say so and lower confidence.
- Do not tell the user to wait for final lineups when confirmed lineups have already been found. Use confirmed lineups directly in the pick instead.
