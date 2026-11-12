# Basketball statistics preview

Direct routes: `/en/sports/basketball` and `/mn/sports/basketball`. Both remain
`noindex`; Sports is hidden from the main navigation pending launch approval.

The browser provides sortable team records, scoring leaders, player averages,
searchable games, game reports, comparisons and CSV downloads. Players CSVs
include the team. Defaults, coverage and comparison options derive from the data.

## Coverage

| Season | Games | Regular | Playoffs | Play-in | Supplied box scores | Review notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2022–23 | 90 | 90 | — | — | 0 | 0 |
| 2023–24 | 156 | 156 | — | — | 0 | 0 |
| 2024–25 | 172 | 130 / 135 | 37 | 5 | 167 | 6 |
| 2025–26 | 175 | 135 | 37 | 3 | 175 | 86 |

There are 593 games across four seasons. The 2022–23 and 2023–24 seasons
are labeled results-only: team records and scoring averages can be compared,
while player, shooting, rebound and assist statistics remain unavailable.
Historical team labels and season-scoped identities are preserved.
No missing playoff games are inferred from the Koo result archives.

Five 2024–25 regular-season results lack box scores;
five regular-season meetings and three known playoff reports are absent.
A supplied box score does **not** mean every field is available or consistent.

The 2025–26 regular season uses all 135 bilingual game pages from the
[league schedule](https://mongolia.basketball/mn/competitions/league/schedule?season=c1a0488c-31a5-429d-8254-3b27aa45e702&type=regular).
It has 3,937 roster entries: 2,882 appearances and 1,055 explicit DNPs.
All 270 player point sums match the recorded final scores and printed team
point totals. This replaces the saved MBA CSV's 3,415 rows, which had point
shortfalls in 201 team-games. MBA-614 Bishrelt Metall now sums to 70, not 44.

198 of those shortfalls reconcile to the previous final scores. Three score
corrections agree across the current header, player sum, team total and final
play-by-play event:

| Game | Team | Previous export | Recorded score |
| --- | --- | ---: | ---: |
| MBA-680 | Darkhan United | 63 | 68 |
| MBA-710 | Darkhan United | 76 | 80 |
| MBA-711 | BCH Knights | 91 | 93 |

Four conflicting website headers in MBA-632, MBA-647 and MBA-657 retain the
previous scores that agree with player and team box-score points. Eight
quarter-total discrepancies in MBA-627, MBA-632, MBA-633 and MBA-735 remain
unchanged and flagged. These four header conflicts, eight quarter conflicts
and three documented score corrections make 15 score-related notes. Another
16 team-games have minute totals outside the displayed-period duration even
allowing one minute of rounding per appearance; overtime information may be
missing or playing times may be wrong. All source times remain visible with
flags. There are 31 regular-season notes and the existing 55 playoff notes. See the committed
`tools/sources/basketball/regular-season-reconciliation.json` and individual
game review notes. Other source conflicts have not been silently repaired.

The league pages provide whole minutes only, without seconds, starters,
offensive/defensive rebound splits, fouls, efficiency or plus/minus. Absent
fields remain null. Active zero-minute rows count as appearances; explicit
DNPs do not. The March 24, 26 and 28, 2026 play-in reports retain 75 roster
entries (63 appearances, 12 DNPs), six totals and their original source images.

English names use the league's supplied Latin spelling where matched.
Unmatched report names use a labeled, deterministic transliteration, which
is not claimed as verified official spelling. Grouping uses team and league
profile within a season, falling back to normalized source name. Full names
match initials only for a unique roster entry within that team. Other spelling
differences remain separate; cross-season identities are not inferred.

Team wins and scoring averages use selected game results. Shooting uses
total makes divided by total attempts. Other averages use the available
box-score sample; any missing value makes that aggregate unavailable.
Player leaderboards require three appearances. The independent validator
checks all 684 supplied team box scores against player points and final scores.

## Source archives and reproduction

Images, screenshots, ZIPs, workbooks and intermediate collections are outside
Git. The browser uses `data.mn/public/sports/basketball.json`; dataset downloads
are generated from that same JSON. Manifests
retain original paths, sizes, SHA-256 hashes, source URLs and retrieval times.
See the [source guide](../tools/sources/basketball/source.md).

The archive is held by the maintainers. Ask a maintainer for a copy. The restore
command below verifies the downloaded ZIP and every source file. The local
backup remains outside the repository.

Separate Koo archives preserve 90 regular-season results for 2022–23
(10 teams, 18 games each) and 156 for 2023–24 (13 teams, 24 games each).
Their results are now included in the browser, without inferred box scores. The 2022–23 source
has 91 entries; its supplied export excludes the April 18 Miners 4–0 Metal
record (ID 19223), retaining it in the audit and original source. Neither
Koo archive supplies player box scores.

Restore into an empty directory, then rebuild:

```powershell
python tools/sources/basketball/restore_archive.py <archive.zip> <archive-directory>
python data.mn/scripts/import-basketball-web.py <archive-directory>/league-web-2025-26 <archive-directory>/outputs/mongolian-basketball-2025-26-regular/data/collection.json <archive-directory>/outputs/mongolian-basketball-2025-26-regular-web
$env:BASKETBALL_ARCHIVE_ROOT = '<archive-directory>/outputs'
node data.mn/scripts/prepare-basketball-preview.mjs
python data.mn/scripts/validate-basketball.py
node --test data.mn/scripts/sports-browser.test.mjs
```

The standard-library importer reparses archived HTML and verifies compressed
and uncompressed hashes, bilingual rows, scoring arithmetic, shooting totals
and final scores. It emits row-aligned EN/MN CSVs. The old CSV importer remains
for historical comparison; its output is no longer used in the browser.
The play-in importer remains reproducible after restoring its source images:
`node data.mn/scripts/import-basketball-playin.mjs`.

Run `npm ci`, `npm run check` and `npm run build` from `data.mn` for clean
website validation. `node data.mn/scripts/export-basketball-preview.mjs`
generates an optional offline preview under the ignored `outputs/` tree.

## Published dataset files

The dataset pages provide a language-matched CSV and a bilingual XLSX:

| Dataset ID | Row grain | Current rows |
| --- | --- | ---: |
| `basketball-game-results` | One recorded game | 593 |
| `basketball-team-records` | One team, season and stage | 65 |
| `basketball-player-game-stats` | One rostered player in one game | 9,082 |

The last dataset includes 1,746 explicit did-not-play rows. Team records use
final scores, so they also cover the two results-only seasons. The player
dataset covers only 2024–25 and 2025–26. Missing statistics stay blank;
source types, public game URLs and review flags are retained. The datasets
are linked from the browser's coverage tab and its Full datasets menu.

Rebuilding downloads and adding a new season from public league pages do not
require the private archive. See **Adding a season** in the
[source guide](../tools/sources/basketball/source.md). After building, run:

```powershell
python tools/sources/basketball/test_public.py
python tools/scripts/validate_dataset.py --all basketball-game-results
python tools/scripts/validate_dataset.py --all basketball-team-records
python tools/scripts/validate_dataset.py --all basketball-player-game-stats
Set-Location data.mn
python ../tools/scripts/validate_vega.py --all
npm run check
npm run build
Set-Location ..
```

## Design references

- https://mdsinabox.com/nba/teams/
- https://mdsinabox.com/nba/teams/okc/
- https://mdsinabox.com/nba/historical_matchups/
