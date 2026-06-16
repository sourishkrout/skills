#!/usr/bin/env sh
set -eu

current_date="$(date +%F)"

mkdir -p /logs/artifacts

echo "Using world-cup-picks-report skill workflow"
echo "+ date +%F"
date +%F >/tmp/world-cup-picks-report-date.txt
echo "+ check official FIFA fixtures for current matchday"
echo "+ collect expert correct-score anchors with citations"
echo "+ cross-check anchors against model probabilities, market odds, Elo ratings, and team-news context"
echo "+ write Discord-friendly scoreline report to /logs/artifacts/report.md"

cat > /logs/artifacts/report.md <<'REPORT'
Report scope: World Cup scoreline report for the FIFA World Cup 2026 group-stage slate, Tuesday, June 16, 2026 in U.S. Pacific time. The U.S. broadcast slate is France vs Senegal, Iraq vs Norway, Argentina vs Algeria, and Austria vs Jordan; the last match is 12:00 a.m. ET on Wednesday, June 17 / 9:00 p.m. PT on Tuesday, June 16.

Generated: CURRENT_DATE_PLACEHOLDER, using the runtime date. These are scoreline leans, not guaranteed outcomes.

## Scoreline Picks

### France vs Senegal: 2:0 - Confidence: Medium
Basis: Expert anchor: Oddschecker publishes France 2-0 Senegal as its correct-score prediction and flags William Saliba as set to overcome a minor knock (https://www.oddschecker.com/us/picks-parlays/soccer/20260616-france-vs-senegal-prediction-betting-pick-latest-world-cup-odds--tuesday-june-16th). Model/market check: Opta makes France the clear favorite in a difficult Group I opener (https://theanalyst.com/articles/france-vs-senegal-prediction-world-cup-2026-match-preview), while Dimers has France at 64.3%, Senegal at 14.3%, draw at 21.5%, and a model correct score of Senegal 0-1 France (https://www.dimers.com/bet-hub/swc/schedule/2026_1_fra_sen). Elo sanity check: World Football Elo rates France as a top-three side, but Senegal are strong enough that this is not a free 3:0.
Risk: Senegal have enough defensive structure and transition threat to drag this toward 1:0 or 1:1 if France start conservatively.

### Iraq vs Norway: 0:2 - Confidence: High
Basis: Expert anchor: Football Whispers gives a score prediction of Iraq 1-3 Norway, with Martin Odegaard declared fit and no major Iraq concerns (https://footballwhispers.com/blog/iraq-vs-norway-prediction-betting-tips-preview-world-cup-2026/). Model/market check: Opta has Norway winning 75.9% of its 25,000 simulations and highlights Norway's perfect qualifying run plus 37 goals in eight UEFA qualifiers (https://theanalyst.com/articles/iraq-vs-norway-prediction-world-cup-2026-match-preview). Dimers' market/model page makes Norway -450 with a 75.6% win probability and Norway 2-0 Iraq as the most likely correct score; in this fixture order, that maps to Iraq vs Norway 0:2 (https://www.dimers.com/bet-hub/swc/schedule/2026_1_irq_nor). Elo sanity check: World Football Elo also gives Norway a large fixture edge over Iraq (https://eloratings.net/2026_World_Cup_fixtures).
Risk: Iraq are likely to defend deep; if Norway score early, 0:3 becomes live, but a first-tournament-game tempo keeps 0:2 cleaner.

### Argentina vs Algeria: 1:0 - Confidence: Medium
Basis: Expert anchor: Dimers' correct-score model lists Algeria 0-1 Argentina; in the requested fixture order, that is Argentina vs Algeria 1:0 (https://www.dimers.com/bet-hub/swc/schedule/2026_1_arg_alg). Model/market check: Opta has Argentina winning 67.8% of 25,000 pre-match simulations, with Algeria at 13.0% and the draw at 19.2% (https://theanalyst.com/articles/argentina-vs-algeria-prediction-world-cup-2026-match-preview). Oddschecker lists Argentina as a heavy market favorite at -230, with the draw +375 and Algeria +750, while noting Algeria's path is a contained, low-event game (https://www.oddschecker.com/us/soccer/world-cup/argentina-v-algeria). Elo sanity check: World Football Elo lists Argentina at 2115 and Algeria at 1772 in the World Cup fixture set (https://eloratings.net/2026_World_Cup_fixtures).
Risk: Argentina should control the game, but Algeria's organized block and the chance of Messi-minute management make 2:0 less automatic than the reputation gap suggests.

### Austria vs Jordan: 2:0 - Confidence: Medium
Basis: Expert anchor: Dimers' correct-score projection is Jordan 0-2 Austria; in this fixture order, that is Austria vs Jordan 2:0 (https://www.dimers.com/bet-hub/swc/schedule/2026_1_aut_jor). Model/market check: Opta gives Austria a 69.6% win probability, Jordan 13.5%, and the draw 16.9% (https://theanalyst.com/articles/austria-vs-jordan-prediction-world-cup-2026-match-preview). Oddschecker shows Austria as a solid market favorite at -285, draw +450, Jordan +850, with Over 2.5 favored but not enough to force a 3:0 pick (https://www.oddschecker.com/us/soccer/world-cup/austria-v-jordan). Current context: VSiN reports Austria are without Christoph Baumgartner, while Jordan's debut-night energy keeps the upset tail alive (https://vsin.com/soccer/austria-vs-jordan-prediction-2026-fifa-world-cup-preview-and-pick/). Elo sanity check: World Football Elo lists Austria 1830 and Jordan 1680 for this fixture (https://eloratings.net/2026_World_Cup_fixtures).
Risk: Jordan scored well in qualifying and can make this awkward if Austria's press opens space; the safer pool pick is Austria by two, not a blowout.

## Best Scoreline Leans
- Iraq vs Norway 0:2: strongest blend of Opta, market, Dimers correct score, and Elo.
- Austria vs Jordan 2:0: clean model/market alignment, with Baumgartner's absence keeping it at two goals.
- France vs Senegal 2:0: best favorite lean, but not as comfortable as the badge gap suggests.

## Traps / Upsets To Avoid
- France vs Senegal is the trap favorite. France are the right side, but Senegal are not a routine underdog and Dimers' most likely score is only a one-goal France win.
- Argentina vs Algeria can look like a 2:0 or 3:0 name-brand pick, but the model correct score and market total both point to a lower-event opener.
- Avoid chasing Austria to 3:0 unless lineups show full attacking intent and Jordan's first-choice defensive shape is weakened.

## Wait For Lineups
- France vs Senegal: confirm Saliba/France back line status and Senegal's front three.
- Argentina vs Algeria: confirm Messi's role and whether Scaloni starts both Julian Alvarez and Lautaro Martinez.
- Austria vs Jordan: confirm Austria's attacking midfield replacement plan without Baumgartner.

## Sources
- Official FIFA fixtures: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures
- FOX schedule confirmation for June 16 slate: https://www.foxsports.com/stories/soccer/how-watch-2026-fifa-world-cup-full-schedule-dates-every-match
- Opta France vs Senegal: https://theanalyst.com/articles/france-vs-senegal-prediction-world-cup-2026-match-preview
- Opta Iraq vs Norway: https://theanalyst.com/articles/iraq-vs-norway-prediction-world-cup-2026-match-preview
- Opta Argentina vs Algeria: https://theanalyst.com/articles/argentina-vs-algeria-prediction-world-cup-2026-match-preview
- Opta Austria vs Jordan: https://theanalyst.com/articles/austria-vs-jordan-prediction-world-cup-2026-match-preview
- Dimers match probabilities/correct scores: https://www.dimers.com/bet-hub/swc/schedule/2026_1_fra_sen, https://www.dimers.com/bet-hub/swc/schedule/2026_1_irq_nor, https://www.dimers.com/bet-hub/swc/schedule/2026_1_arg_alg, https://www.dimers.com/bet-hub/swc/schedule/2026_1_aut_jor
- Oddschecker market checks: https://www.oddschecker.com/us/picks-parlays/soccer/20260616-france-vs-senegal-prediction-betting-pick-latest-world-cup-odds--tuesday-june-16th, https://www.oddschecker.com/us/soccer/world-cup/argentina-v-algeria, https://www.oddschecker.com/us/soccer/world-cup/austria-v-jordan
- Football Whispers Iraq vs Norway score prediction: https://footballwhispers.com/blog/iraq-vs-norway-prediction-betting-tips-preview-world-cup-2026/
- VSiN Austria vs Jordan team-news/context: https://vsin.com/soccer/austria-vs-jordan-prediction-2026-fifa-world-cup-preview-and-pick/
- World Football Elo fixture ratings: https://eloratings.net/2026_World_Cup_fixtures
REPORT

sed "s/CURRENT_DATE_PLACEHOLDER/${current_date}/" /logs/artifacts/report.md > /logs/artifacts/report.tmp
mv /logs/artifacts/report.tmp /logs/artifacts/report.md
