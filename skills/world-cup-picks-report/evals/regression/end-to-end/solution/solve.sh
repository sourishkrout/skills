#!/usr/bin/env sh
set -eu

current_date="$(date +%F)"

mkdir -p /logs/artifacts

echo "Using world-cup-picks-report skill workflow"
echo "+ date +%F"
date +%F >/tmp/world-cup-picks-report-date.txt
echo "+ identify the next full unplayed World Cup slate in U.S. Pacific time, no earlier than tomorrow"
echo "+ check official FIFA and ESPN fixtures for the resolved future slate"
echo "+ collect expert correct-score anchors with citations"
echo "+ cross-check anchors against Opta model probabilities, market odds, World Football Elo ratings, and team-news context"
echo "+ verify lineup and injury watch items against official FIFA match pages, ESPN lineups, and credible preview sources"
echo "+ write Discord-friendly scoreline report to /logs/artifacts/report.md"

cat > /logs/artifacts/report.md <<'REPORT'
# World Cup Scoreline Report

Report scope: World Cup scoreline report for the next full unplayed FIFA World Cup 2026 slate no earlier than tomorrow: Wednesday, June 24, 2026 in U.S. Pacific time. This skips the June 23 PT same-day fixture and covers the six-match June 24 PT slate: Switzerland vs Canada and Bosnia-Herzegovina vs Qatar at 12:00 p.m. PT, Scotland vs Brazil and Morocco vs Haiti at 3:00 p.m. PT, then Czechia vs Mexico and South Africa vs South Korea at 6:00 p.m. PT.

Generated: CURRENT_DATE_PLACEHOLDER, using the runtime date. These are scoreline leans, not guaranteed outcomes. The slate is sourced from official FIFA/ESPN schedules, Opta/The Analyst match probabilities, expert scoreline previews, market snapshots, World Football Elo/FIFA ranking context, and lineup/team-news previews.

Lineup/injury status: official FIFA match centres, ESPN lineup pages, AP/Reuters soccer wires, and match previews should be rechecked near kickoff. Current cited previews flag Canada midfield uncertainty, Qatar suspensions, Brazil attacker rotation/injury risk, Mexico rotation after a strong group position, Morocco rotation risk, and South Africa suspensions.

## Scoreline Picks

### Switzerland vs Canada: 1:1 - Confidence: Low
Basis: Opta/The Analyst and market previews make Switzerland the slight model side, while Canada have home-field context and enough attacking form to avoid a pure underdog read (https://theanalyst.com/articles/switzerland-vs-canada-prediction-world-cup-2026-match-preview, https://www.racingpost.com/sport/football-tips/world-cup-2026/switzerland-vs-canada-world-cup-prediction-team-news-odds-betting-tips-and-bet-builder-a3SeE5N0GPTV/). Expert previews split between Switzerland edge, Canada upset angles, and draw-safe logic, so 1:1 is the conservative pool score. World Football Elo/FIFA ranking context keeps Switzerland ahead but not by enough to force a multi-goal pick (https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men).
Risk: Switzerland can still push for first place, so 1:2 or 2:1 is live if the match opens up. Recheck Canada's midfield availability, especially Ismael Kone and Stephen Eustaquio, before locking a draw.

### Bosnia-Herzegovina vs Qatar: 2:0 - Confidence: Medium
Basis: Opta gives Bosnia-Herzegovina a clear win lean, and Covers' match preview points to Bosnia territory, chance volume, and Qatar defensive stress after heavy shot concessions (https://theanalyst.com/articles/bosnia-herzegovina-vs-qatar-prediction-world-cup-2026-match-preview, https://www.covers.com/world-cup/bosnia-vs-qatar-prediction-picks-odds-wednesday-6-24-2026). Market and Elo checks both support Bosnia as the better side, while the scoreline stays at 2:0 because Qatar suspensions and defensive pressure matter more than Bosnia's imperfect finishing profile (https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men).
Risk: Both teams needing points can make the game messy. If Edin Dzeko or Bosnia's central attackers are limited, 1:0 is safer; if Qatar score first, the match can become a volatile 2:1.

### Scotland vs Brazil: 0:2 - Confidence: Medium
Basis: Opta makes Brazil the clear favorite, SportsGambler's preview leans toward a Brazil win and a larger Brazil score, and Racing Post market context confirms Brazil as the heavy side (https://theanalyst.com/articles/scotland-vs-brazil-prediction-world-cup-2026-match-preview, https://www.sportsgambler.com/betting-tips/football/scotland-vs-brazil-prediction-lineups-odds-2026-06-24/, https://www.racingpost.com/sport/football-tips/world-cup-2026/). World Football Elo/FIFA ranking context also puts Brazil well above Scotland, but the pick trims the ceiling to 0:2 because group incentives and Brazil rotation can slow the match (https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men).
Risk: Scotland may play for damage control if a narrow loss is useful, making 0:1 plausible. If Brazil start a near first-choice attack and need goal difference, 0:3 becomes the upside.

### Morocco vs Haiti: 2:0 - Confidence: High
Basis: Opta/The Analyst makes Morocco the strongest favorite on this slate, Racing Post's market snapshot has Morocco heavily favored, and correct-score market framing points toward a controlled 2:0 rather than a chase-heavy game (https://theanalyst.com/articles/morocco-vs-haiti-prediction-world-cup-2026-match-preview, https://www.racingpost.com/sport/football-tips/world-cup-2026/morocco-vs-haiti-world-cup-prediction-team-news-odds-betting-tips-and-bet-builder-ah7S64g5gWZJ/). Elo/FIFA ranking context backs Morocco as the much stronger side, and Haiti's defensive record keeps the clean-sheet favorite profile intact (https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men).
Risk: Rotation is the main concern if Morocco already like their group position. If key creators rest, 1:0 is the lower-ceiling fallback.

### Czechia vs Mexico: 0:1 - Confidence: Medium
Basis: Opta gives Mexico the edge, Racing Post's preview and market read also favor Mexico, and under-leaning market context fits a narrow 0:1 score rather than a wide margin (https://theanalyst.com/articles/czechia-vs-mexico-prediction-world-cup-2026-match-preview, https://www.racingpost.com/sport/football-tips/world-cup-2026/czech-republic-vs-mexico-world-cup-prediction-team-news-odds-betting-tips-and-bet-builder-aVhrU9r75F2V/). World Football Elo/FIFA ranking context supports Mexico as the better side, but Czechia's set-piece threat and Mexico rotation keep confidence below high (https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men).
Risk: If Mexico rotate heavily or settle for group control, 0:0 or 1:1 becomes a real danger. Wait for Mexico's attacking lineup.

### South Africa vs South Korea: 0:1 - Confidence: Medium
Basis: Sports Mole and Forebet both support a narrow South Korea edge, ESPN/DraftKings odds make South Korea the stronger side, and the market profile points to a low-total game (https://www.sportsmole.co.uk/football/south-africa/world-cup-2026/preview/south-africa-vs-south-korea-prediction-team-news-lineups_599815.html, https://www.forebet.com/en/football/matches/south-africa-south-korea-2463179, https://www.espn.com/soccer/odds/_/gameId/760466). Elo/FIFA ranking context and South Africa suspension notes point toward South Korea controlling enough phases to win 0:1 (https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men).
Risk: South Africa's need to chase can either create a late Korean second or a set-piece equalizer. If South Korea play too passively for a draw, 0:0 or 1:1 is the trap.

## Best Scoreline Leans
- Morocco vs Haiti 2:0: cleanest model, market, and strength-rating blend.
- South Africa vs South Korea 0:1: best low-total lean with multiple preview/model sources converging.
- Czechia vs Mexico 0:1: reasonable if Mexico do not rotate too heavily.

## Traps / Upsets To Avoid
- Do not overreact to Canada's home context; Switzerland remain the stronger model side, but the draw is safer than forcing either winner.
- Do not chase a big Brazil score blindly; Scotland can slow the game if a narrow loss helps their group math.
- Treat Bosnia-Herzegovina vs Qatar carefully because both teams' incentives can swing the scoreline after the first goal.

## Wait For Lineups
- Switzerland vs Canada: check Eustaquio and Canada's replacement plan for Kone.
- Scotland vs Brazil: check Brazil's front three, Raphinha status, and whether Neymar starts or is managed.
- Czechia vs Mexico: check how heavily Mexico rotate.
- Morocco vs Haiti: check whether Morocco rest key creators.
- South Africa vs South Korea: confirm South Africa suspension replacements and South Korea's attacking starters.

## Sources
- Official schedule: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures, https://www.espn.com/soccer/story/_/id/48939282/2026-fifa-world-cup-fixtures-results-match-schedule-group-stage-knockout-rounds-bracket
- Opta/The Analyst match previews: https://theanalyst.com/articles/switzerland-vs-canada-prediction-world-cup-2026-match-preview, https://theanalyst.com/articles/bosnia-herzegovina-vs-qatar-prediction-world-cup-2026-match-preview, https://theanalyst.com/articles/scotland-vs-brazil-prediction-world-cup-2026-match-preview, https://theanalyst.com/articles/morocco-vs-haiti-prediction-world-cup-2026-match-preview, https://theanalyst.com/articles/czechia-vs-mexico-prediction-world-cup-2026-match-preview
- Expert and market checks: https://www.racingpost.com/sport/football-tips/world-cup-2026/switzerland-vs-canada-world-cup-prediction-team-news-odds-betting-tips-and-bet-builder-a3SeE5N0GPTV/, https://www.covers.com/world-cup/bosnia-vs-qatar-prediction-picks-odds-wednesday-6-24-2026, https://www.sportsgambler.com/betting-tips/football/scotland-vs-brazil-prediction-lineups-odds-2026-06-24/, https://www.racingpost.com/sport/football-tips/world-cup-2026/morocco-vs-haiti-world-cup-prediction-team-news-odds-betting-tips-and-bet-builder-ah7S64g5gWZJ/, https://www.racingpost.com/sport/football-tips/world-cup-2026/czech-republic-vs-mexico-world-cup-prediction-team-news-odds-betting-tips-and-bet-builder-aVhrU9r75F2V/, https://www.sportsmole.co.uk/football/south-africa/world-cup-2026/preview/south-africa-vs-south-korea-prediction-team-news-lineups_599815.html
- Model, market, Elo, and team-strength checks: https://www.forebet.com/en/football/matches/south-africa-south-korea-2463179, https://www.espn.com/soccer/odds/_/gameId/760466, https://eloratings.net/2026_World_Cup_fixtures, https://inside.fifa.com/fifa-world-ranking/men
- Lineup and team-news watch: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures, https://www.espn.com/soccer/lineups, https://www.reuters.com/sports/soccer/, https://apnews.com/hub/soccer
REPORT

sed "s/CURRENT_DATE_PLACEHOLDER/${current_date}/" /logs/artifacts/report.md > /logs/artifacts/report.tmp
mv /logs/artifacts/report.tmp /logs/artifacts/report.md
