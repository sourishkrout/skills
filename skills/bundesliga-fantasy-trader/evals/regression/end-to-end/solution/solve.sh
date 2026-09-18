#!/usr/bin/env sh
set -eu

artifacts_dir="${RUNME_ARTIFACTS_DIR:-/logs/artifacts}"
mkdir -p "$artifacts_dir"

echo "Using bundesliga-fantasy-trader frozen Matchday 4 workflow"
echo "+ read injected skill and 2026/27 rules transcript"
echo "+ read snapshot/squad.md and snapshot/evidence.md"
echo "+ preserve the September 17, 2026 evidence cutoff"
echo "+ write proposed transfer plan to $artifacts_dir/report.md"

cat > "$artifacts_dir/report.md" <<'REPORT'
# Bundesliga Fantasy Matchday 4 Plan

Evidence cutoff: Thursday, September 17, 2026, 8:48 a.m. America/Los_Angeles. Matchday 4 is treated as upcoming. Kane's 37.18M and Olise's 37.41M sell values and the 3.34M bank are observed; all other player prices are dated estimates or unknown live values.

## What to do now

Try this highest-potential slate in order: first stage Ebnoutalib → Hložek, then stage Juranović → Katić. If the app reports that it is unaffordable, return with the shortfall and revise the lowest-impact move.

1. **Proposed:** Younes Ebnoutalib → Adam Hložek. Ebnoutalib is projected for only 30 minutes and 60 points, while Hložek has 183 projected points in the round's second-strongest attacking fixture ([TheFantasyTool, model data September 14](https://thefantasytool.com/previews/bundesliga-fantasy-matchday-4-captain-picks-best-buys)).
2. **Proposed:** Josip Juranović → Nikola Katić. Union face Bayern's slate-leading 3.81 expected goals, while Katić is a 5.9M estimated route into the round's third-best clean-sheet line ([TheFantasyTool, model data September 14](https://thefantasytool.com/previews/bundesliga-fantasy-matchday-4-captain-picks-best-buys)).
3. Set **3-5-2**. Provisional stars: **Jordy Makengo (DEF), Michael Olise (MID), Harry Kane (FOR)**. Makengo's official Matchday 3 Top 11 place supplies the strongest corroborated defender signal; the later pre-cutoff refresh restores Olise and Kane to the top overall tier, so hold both despite the older rotation warning ([Bundesliga Matchday 3 Top 11, September 14](https://www.bundesliga.com/de/bundesliga/news/fantasy-manager-top-elf-spieltag-saison-2026-27-punkte-beste-spieler-spieltag-3-39183); [TheFantasyTool player-picks refresh](https://thefantasytool.com/player-picks-bl)).

**Deadline:** Friday, September 18, 2026 at **20:30 CEST / 18:30 UTC / 11:30 a.m. America/Los_Angeles (PDT)** ([DFB Matchday 4 schedule](https://datencenter.dfb.de/datencenter/bundesliga/2026-2027/4)).

## Squad baseline

Confirmed: 15 players, 3.34M bank, 0/5 transfers used, 155.13M displayed squad market value. The total market value is not treated as bank. Rønnow's app warning remains unresolved because the snapshot has no qualifying diagnosis; this package therefore prioritizes the evidence-backed minutes and fixture problems instead of declaring him ruled out.

## Full-squad audit

| Player | Proposed treatment | Frozen evidence and rationale |
|---|---|---|
| Fabian Bredlow | Start | Scored 121 in Matchday 3; he is the available baseline while Rønnow carries an unresolved app warning. |
| Frederik Rønnow | Bench; recheck warning | The app warning is observed, but the dossier contains no diagnosis or return date, so he is not called ruled out. |
| Josha Vagnoman | Bench | Keep rather than spend a third transfer; Stuttgart face a Dortmund side that entered the round on nine points ([DFB/pre-round standings snapshot](https://datencenter.dfb.de/datencenter/bundesliga/2026-2027/4)). |
| Jordy Makengo | Start, DEF star | His official Matchday 3 Top 11 place and 336 points supply the strongest corroborated defender signal, despite the tougher Frankfurt fixture ([Bundesliga Matchday 3 Top 11, September 14](https://www.bundesliga.com/de/bundesliga/news/fantasy-manager-top-elf-spieltag-saison-2026-27-punkte-beste-spieler-spieltag-3-39183)). |
| Keita Kosugi | Start, hold | The September 14 model called him its best-value defender at 3.6M estimated and 109 projected points; treat that as a supplementary value signal, not authoritative evidence ([TheFantasyTool preview](https://thefantasytool.com/previews/bundesliga-fantasy-matchday-4-captain-picks-best-buys)). |
| Josip Juranović | Sell | Union had conceded ten before visiting a Bayern attack projected for 3.81 goals; Katić also lowers the estimated price ([TheFantasyTool preview](https://thefantasytool.com/previews/bundesliga-fantasy-matchday-4-captain-picks-best-buys)). |
| Michael Olise | Start, MID star | Hold the observed 37.41M asset: the later pre-cutoff refresh ranked him in the top three, although the older model warned of rotation ([player-picks refresh](https://thefantasytool.com/player-picks-bl)). |
| Ezechiel Banzuzi | Start, hold | His confirmed 243 Matchday 3 points and inclusion in Bulinews' prior scout recommendations corroborate the supplementary model's low-cost hold signal ([Bulinews, September 11](https://bulinews.com/fantasy-bundesliga-scout-squads-for-matchday-3-2)). |
| Yuito Suzuki | Start, hold | The snapshot supplies no player-specific reason to sell; retain him while using transfers on the quantified minutes and fixture weaknesses. |
| Ethan Nwaneri | Start, hold | The snapshot supplies no player-specific reason to sell; retain him rather than manufacture a third transfer. |
| Adil Aouchiche | Start, hold | His confirmed 233 Matchday 3 points and inclusion in Bulinews' prior scout recommendations corroborate the supplementary 156-point projection for the Elversberg fixture ([Bulinews, September 11](https://bulinews.com/fantasy-bundesliga-scout-squads-for-matchday-3-2)). |
| Hugo Bolin | Bench, hold | His 20 Matchday 3 points make him the least compelling of the retained midfielders; no frozen player-specific evidence justifies paying for a sale. |
| Marin Ljubičić | Bench, hold | His 55 Matchday 3 points and Union's trip to the slate's strongest projected opponent argue against the XI, but his dated 2.8M price limits the value of a speculative extra transfer ([Bulinews, September 11](https://bulinews.com/fantasy-bundesliga-scout-squads-for-matchday-3-2)). |
| Harry Kane | Start, FOR star | Hold the observed 37.18M asset: the later refresh ranked him in the top three and Bayern have the slate's strongest attack, while the older rotation downgrade is acknowledged ([player-picks refresh](https://thefantasytool.com/player-picks-bl)). |
| Younes Ebnoutalib | Sell | The model projects only 30 minutes, a 0.25 starter factor, and 60 points, making this the clearest minutes upgrade ([TheFantasyTool preview](https://thefantasytool.com/previews/bundesliga-fantasy-matchday-4-captain-picks-best-buys)). |

## Recommended package

- Ebnoutalib sale value: **unknown live**, `5.5M estimated`.
- Juranović sale value: **unknown live**, `6.43M observed September 11`.
- Hložek purchase price: `9.2M estimated`.
- Katić purchase price: `5.9M estimated`.

At the dated estimates, the two sales plus the 3.34M bank narrowly cover the two estimated purchases. The live sale values are unknown, so try this slate first and report the app's shortfall if it does not fit; do not collect every sell value in advance. It uses 2 of 5 transfers, retains 2 GK / 4 DEF / 6 MID / 3 FOR, and leaves every club at or below three players.

## Formation and stars

**Formation: 3-5-2**

- GK: Fabian Bredlow
- DEF: Keita Kosugi, Nikola Katić, Jordy Makengo ★
- MID: Michael Olise ★, Adil Aouchiche, Ezechiel Banzuzi, Yuito Suzuki, Ethan Nwaneri
- FOR: Harry Kane ★, Adam Hložek
- Bench: Frederik Rønnow, Josha Vagnoman, Hugo Bolin, Marin Ljubičić

Makengo's official 336-point Matchday 3 performance earns the defender star, while Kosugi's 109-point model projection supports starting him. Olise and Kane remain provisional stars subject only to pre-deadline lineup confidence; the snapshot contains competing projections, so neither is presented as rotation-proof. TheFantasyTool is supplementary throughout: its prices and projections are estimates, its internal data is unsupported, and its captain terminology does not define the app's three-star system.

All moves above remain proposed. No transfer has been executed or completed.
REPORT
