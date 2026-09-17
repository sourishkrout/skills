---
name: "bundesliga-fantasy-trader"
description: "Research and manage Bundesliga Fantasy squads, transfers, formations, Top 11 lineups, star picks, budgets, and deadline checks. Use this skill whenever the user asks for Bundesliga Fantasy advice, a squad review, matchweek planning, player trades, or a final pre-deadline check."
---

# Bundesliga Fantasy Trader

## Operating principles

- Confirm the previous matchweek's complete squad before giving squad-dependent advice. A recommendation built on an assumed squad can be legal on paper and useless in the app.
- Browse current external sources for every matchweek. Memory and prior reports are starting points, not evidence.
- Support every actionable recommendation with current expert analysis. Fixture or availability facts alone do not justify a fantasy recommendation.
- Treat trades as an iterative decision with the user. Explain meaningful downside, then respect an informed risk preference when it remains legal.
- Do the budget iteration yourself. Give the strongest best-effort transfer package available from current evidence, and automatically replace or reorder targets when the first package is too expensive. Do not make the user shuttle screenshots merely to perform arithmetic or discover ordinary player prices.
- Keep proposed and completed actions distinct. Only a user confirmation or authoritative post-transfer screenshot proves completion.

Pure rules, fixture, or deadline questions may be answered without completing the squad-confirmation gate.

## Source authority

Use direct pages rather than search-result links and include publication or update dates when available.

1. [Bundesliga.com](https://www.bundesliga.com/en/bundesliga) and the [DFB Datencenter](https://datencenter.dfb.de/) for published rules, fixtures, and deadlines.
2. The Bundesliga app for current in-app rules and the user's live squad, player positions, prices, sell values, budget, and transfer legality.
3. [Bulinews Fantasy](https://bulinews.com/fantasy) as the primary source for expert picks, scout squads, predicted XIs, and Fantasy Show analysis.
4. [LigaInsider](https://www.ligainsider.de/), official club reports and press conferences, and [FotMob](https://www.fotmob.com/leagues/54/overview/bundesliga) to corroborate lineup and availability claims.
5. [TheFantasyTool](https://thefantasytool.com/optimal-teams-bl) as an occasional projection and value-model supplement.

Resolve source conflicts by subject:

- Prefer the newest dated Bundesliga or DFB publication for published rules and schedules.
- Prefer the Bundesliga app when its current rule text or enforced behavior differs from an article, and for all live game state.
- Prefer official club news for a player's confirmed availability.
- Report material expert disagreement instead of silently choosing one view.

### TheFantasyTool limitations

When using or summarizing TheFantasyTool, make these limitations clear and concise:

- Full rankings, the personalized transfer solver, and the optimal-team calculator require a paid subscription or credit-card trial. Public access is limited to previews, selected projections, predicted lineups, and partial rankings.
- The site has no documented public developer API. Its internal endpoints, including `/api/games`, `/api/core_players`, `/api/schedule`, `/api/lineups`, and `/api/xp_filtered_players`, may be used as best-effort data sources, but they are unsupported and may change, become restricted, or require authentication. On an HTTP error, authentication failure, schema mismatch, missing required field, or incomplete response, stop API-dependent processing and report the error; never silently treat failed or partial data as valid. A clearly disclosed fallback to published pages or another source is allowed.
- Its projections are probabilistic and may change with betting odds, injuries, and lineup news. They cannot reliably anticipate rotation, early substitutions, injuries, or cards.
- Confidence is lower for newly promoted teams and recent transfers because less historical data is available.
- Its displayed rules may not exactly match Bundesliga Fantasy; for example, references to captains do not reflect the app's three-star system.
- Treat it as one supplementary input. Cross-check its output against current Bundesliga app rules, official lineup and availability information, and independent fantasy analysis before recommending an action.

## Workflow

### 1. Confirm the previous matchweek's full squad

Make a best effort to recover the previous squad from memory, the latest squad log, recent matchweek notes, and screenshots. Prefer a full-team screenshot over reconstructed conversation history.

Do not use `browser-use` or independently explore bundesliga.com to recover or confirm the previous matchweek's squad. Those methods do not satisfy this confirmation gate; rely on user-provided screenshots, the squad log, prior conversation records, and the user's explicit confirmation or correction.

Present a `Previous squad confirmation` block containing all 15 players, with each player's app position and club, plus the known bank. Mark unknown or disputed entries explicitly; never fill a gap by guessing. Even when the user supplied a screenshot, restate the squad so the baseline is unambiguous.

Ask the user to confirm or correct the full squad. Do not provide squad-dependent recommendations until the user explicitly confirms the 15-player baseline. Current-source research may proceed while confirmation is pending.

**Done when:** the user has explicitly confirmed or corrected all 15 players.

### 2. Establish the rules and deadline

Before checking a squad or transfer package, read sections 2-4 of [the authoritative 2026/27 app rules transcript](references/rules-2026-27.md). Load sections 5-7 only when the user asks about leagues, league formats, or prizes. If the season has changed, a rule is unclear, or current app behavior conflicts with the transcript, verify the current in-app rules. The current app rule wins; disclose the change and flag the bundled transcript for updating.

Verify the target matchweek and first kickoff through Bundesliga.com, with the DFB Datencenter as the schedule cross-check. Treat the first kickoff as the transfer, formation, lineup, and star deadline unless newer official rules state otherwise. Show the fixture's local time, UTC, and `America/Los_Angeles`.

**Done when:** the applicable rules, matchweek, first fixture, and exact deadline are explicit and current.

### 3. Gather current expert and team evidence

Check current Bundesliga probable XIs and injury information, then Bulinews matchweek analysis. Use LigaInsider, club reports or pressers, and FotMob to resolve late lineup uncertainty. Use TheFantasyTool when its projections add meaningful value context.

Distinguish confirmed XI, probable XI, doubtful, and ruled out. Record direct links and update dates. Assess the minutes and availability of every current squad member and shortlisted target.

For each potential action, find at least one current source that supplies fantasy analysis, an expert pick, a scout recommendation, or a projection. Bundesliga/DFB fixture data, app data, injury reports, and probable lineups can support facts but do not, by themselves, satisfy the expert-analysis requirement. Seek a second analytical source when available and state meaningful disagreement.

If no qualifying expert analysis supports an action, identify the evidence gap and withhold that recommendation.

**Done when:** every candidate action has current team evidence and at least one qualifying expert-analysis source.

### 4. Audit the confirmed squad

Flag ruled-out players, probable non-starters, and structural problems first. Then assess role, fixture, club concentration, bench quality, and value. Preserve healthy premium assets unless current expert evidence supports a materially better use of the slot or budget.

Separate mandatory fixes, upside moves, and budget enablers. Cite each proposed sell, hold, or priority decision directly beside the claim that supports it.

**Done when:** each outgoing or retained priority has a current, cited rationale.

### 5. Build and iterate legal trade packages

Use the freshest prices available. Prefer, in order: live values visible in an accessible signed-in Bundesliga app session; app values already supplied in the conversation or squad log; then current prices from direct, dated sources. An overall squad market value is useful context but is not interchangeable with bank or individual sell values. Never assume an older article's price is still exact.

Do not stop at the first unaffordable package. Build a small ranked target pool internally, then solve the package iteratively:

1. Price the preferred package and show `sale proceeds + bank - purchase cost = remaining bank`.
2. If it is over budget, preserve mandatory minutes fixes and the highest-impact incoming player; downgrade the lowest-marginal-value move first.
3. Recalculate after each substitution until the package is feasible. Also check squad composition, club limit, transfer allowance, likely formation, and star options on every pass.
4. Return one best feasible package plus, only when useful, one cheaper fallback. If prices are estimates, prefer a reasonable safety margin instead of spending to an apparent zero.

When a signed-in app session is accessible, inspect the transfer market and current squad values directly and use the transfer builder to test combinations if this can be done without confirming or submitting transfers. Treat staged selections as provisional and never execute a transfer without the user's authorization.

If exact live values remain inaccessible, still make a best-effort proposal from the freshest sourced or previously observed values. Label each price as `live`, `observed at <date/time>`, or `estimated`; show the uncertainty and state whether the package is definitely feasible, feasible with a stated buffer, or conditional on a specific value. Prefer alternatives comfortably below the inferred ceiling.

Present concrete player-for-player trades, not a menu of targets. Lead with one `Recommended package` in execution order. Add at most one `Fallback package`, and only when a doubtful player, price threshold, or materially different risk choice makes it useful. State exactly what triggers the fallback. Keep the broader target pool and rejected combinations out of the user-facing answer unless the user asks for them. Label all moves `Proposed`, not completed. Cite every incoming, outgoing, hold, and spend-or-bank recommendation inline with current expert analysis.

Invite the user to choose tradeoffs such as minutes security versus upside, short-term fixture strength versus longer horizon, concentrated club exposure versus diversification, and spending versus preserving bank.

When the user's preference carries a material downside:

1. Push back once with the relevant evidence and concrete consequence.
2. If the user accepts the risk and the package remains legal, record it as an `Accepted risk` and optimize the remaining moves around it.
3. Do not repeatedly relitigate an informed choice unless new evidence changes the risk.

After every revision, rerun the full legality, budget, evidence, formation, and star checks. Missing price certainty is not a reason to withhold a package. Ask for user input only after exhausting accessible live state, recent conversation evidence, the squad log, and current direct sources, and only when the remaining uncertainty can change which package is legal. Request the smallest missing datum—such as bank and one or two sell values, preferably as text—while giving the provisional package and the exact threshold at which its fallback should be used. Do not request a transfer-builder screenshot by default.

**Done when:** the user has a cited package that is verified feasible or is explicitly conditional on minimal named price data, with an automatically computed fallback for the adverse case.

### 6. Set formation, Top 11 shape, bench, and stars

Choose the formation that exposes the strongest scoring pool under Top 11 mode. Name the provisional XI and bench, then select one defender, midfielder, and forward star. Account for the risk that a star outside the Top 11 receives no transferred bonus, and prefer confirmed or highly secure starters.

Cite the formation, XI/bench, and each star recommendation with current expert analysis. Revisit them whenever the trade package changes.

**Done when:** formation, XI, bench, and all three stars are explicit, current, and cited.

### 7. Deliver the matchweek report

Lead with `What to do now`: a compact numbered list of exact player-out → player-in trades in execution order, followed by the provisional formation and stars when relevant. Give one recommended package and no more than one clearly triggered fallback; do not group multiple replacement targets by price or role. Name any action that should wait for lineup news. End the block with a single `Deadline` line and any short-horizon context that materially changes the plan.

Use action verbs and compact phrases. Keep rationale to one sentence per action, place citations beside the action they support, and do not repeat the research narrative before giving the recommendation. If live prices, bank, or legality are missing, lead with the best-effort package, its price-confidence labels, budget threshold, and cheaper fallback. Then request only the minimal numeric value that would resolve a consequential uncertainty.

For a full report, follow the action block with only the applicable supporting sections:

1. `Squad baseline` - confirmation status and bank.
2. `Proposed transfers` - live prices, arithmetic, and concise rationale not already stated.
3. `Accepted risks and fallbacks` - user-selected tradeoffs and contingency actions.
4. `Legality and budget` - transfer count, squad composition, club limit, and remaining bank.
5. `Formation and stars` - formation, XI/bench, and cited stars.
6. `Sources` - direct links with publication or update dates.

Keep Discord output concise, omit inapplicable sections, avoid tables, and wrap multiple bare links in angle brackets. Never spend merely to reach zero, and never present an unsupported action as a recommendation.

### 8. Re-check and persist when requested

For a deadline re-check, schedule a one-shot automation relative to the verified first kickoff, normally two hours before lock. Include the proposed transfers, accepted risks, bank, source pages, squad-log path, players needing verification, and destination Discord channel. Require a concise **GO** or **CHANGE** verdict with only actionable, cited changes.

After explicit user confirmation or a final screenshot, append the matchweek squad, completed transfers, bank, formation, bench, stars, accepted risks, and evidence date to the squad log. Preserve earlier matchweeks and correct prior reconstructions when stronger evidence contradicts them.

## Final verification

Before delivering a squad-dependent recommendation, confirm that:

- the user explicitly confirmed all 15 players in the previous-matchweek squad;
- the current rules reference was read and any newer official rule was reconciled;
- every actionable recommendation has an adjacent, current expert-analysis citation;
- factual lineup and availability claims use the source hierarchy and accurate certainty labels;
- every player position, squad constraint, club limit, and transfer count is app-legal, and price/budget claims are either live-verified or clearly labeled with their source, uncertainty, threshold, and fallback;
- kickoff and deadline conversions agree;
- accepted user risks are recorded without being presented as the evidence-led default;
- completed transfers are not claimed without explicit confirmation.
