# Mongolian Basketball Game Results

- ID: `basketball-game-results` (permanent; do not rename)
- Source: `basketball`
- Category: Sports / Спорт
- Grain: one recorded game
- Current rows: 593
- Input: `data.mn/public/sports/basketball.json`

## Build

```sh
python tools/sources/basketball/build_public.py
python tools/sources/basketball/register.py
```

The builder derives both languages from the same ordered record list. It writes
`basketball-game-results-en.csv`, `basketball-game-results-mn.csv` and `basketball-game-results.xlsx` to `data.mn/public/datasets/`.
The XLSX uses the canonical download writer, with English and Монгол sheets.
The documented event/record-table exception preserves the specified row grain
and all measures instead of pivoting away teams, players, sources or review flags.

## Fields and provenance

`source_type` uses `league page`, `koo archive` or `transcribed image`.
Source URLs are identical across language files and prefer the public English
game page; image filenames and date-only corroboration links are not substituted
for a public box-score page. `review_flag` is 1 if the game has any review issue,
otherwise 0. It does not assert that the final score is incorrect.
Team aggregates inherit a flag from any included game; their `source_url` is
empty because the aggregate has no single public page. If multiple source types
contribute to a team aggregate, `source_type` lists each type separated by `; `.

Team wins and losses come only from recorded final scores, not published league
standings. Scoring averages divide total points by recorded games and are rounded
to six decimal places. Historical team IDs remain season-specific; sponsor/name
similarity does not establish franchise continuity.

Player rows preserve all supplied statistics, nulls, minutes strings and explicit
did-not-play records. Exclude `did_not_play = 1` from appearance-based averages.
`player_id` is scoped by season and team; do not join on player name alone.
`name_source` distinguishes league spelling, source report spelling and transliteration.

## Coverage

The 2022–23 and 2023–24 seasons contain results only, with no player box scores. The 2024–25 collection has 172 recorded games: 167 have box scores and five have only results. Its reports and result posters were transcribed from images. The 2025–26 collection has 175 recorded games with box scores: 135 regular-season games from bilingual league pages, plus 37 playoff and three play-in games transcribed from images. These counts describe the recorded collection, not a claim that every season is complete.

Missing source fields stay empty, not zero. Review flags identify games with documented source inconsistencies; a flag does not necessarily indicate a scoring discrepancy. All 684 supplied team box scores reconcile player points with team totals and recorded final scores. English names use the league spelling where available; other names are transliterations and are not verified official spellings.
