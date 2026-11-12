# Mongolian basketball

- Source ID: `basketball`
- Type: mixed (public bilingual league pages, Koo results archives, transcribed images)
- Public source: https://mongolia.basketball/
- Historical results: https://www.koo.mn/basketball/men/results/
- Update frequency: after reviewed game reports

The preview combines publicly published Mongolian Basketball Association pages,
supplied FIBA reports, and Koo season exports. The archive is held by the
maintainers. Ask a maintainer for a copy.

## Files retained in Git

- `archive-manifest.json`: 718 source paths, byte lengths and SHA-256 hashes.
- `archive-package.json`: ZIP filename, length, SHA-256, and maintainer-held
  status.
- `league-pages-manifest.json`: original URLs, UTC retrieval times and hashes
  for saved schedule/game pages.
- `game-id-mapping.json`: reviewed website-to-MBA IDs, checked against date
  and team order during import.
- `conflicting-score-play-by-play.json`: final events used in score review,
  auditable against the original saved HTML.
- `regular-season-reconciliation.json`: all 270 team-game score comparisons.
- `regular-season-validation.json`: generated import counts.

Manifests preserve provenance and content hashes, not public archive URLs.
Raw images, screenshots, ZIPs, workbooks, and intermediate collections are
outside Git. The site needs only the public browser JSON and published dataset
files. The archive is held by the maintainers. Ask a maintainer for a copy.

## Restore and rebuild the reviewed archive

Use a working copy of the archive obtained from a maintainer. The restore
command verifies the ZIP and every archived file against the committed hashes.
Use an empty destination; differing existing files are never overwritten.

```powershell
python tools/sources/basketball/restore_archive.py <archive.zip> <archive-directory>
python data.mn/scripts/import-basketball-web.py <archive-directory>/league-web-2025-26 <archive-directory>/outputs/mongolian-basketball-2025-26-regular/data/collection.json <archive-directory>/outputs/mongolian-basketball-2025-26-regular-web
$env:BASKETBALL_ARCHIVE_ROOT = '<archive-directory>/outputs'
node data.mn/scripts/prepare-basketball-preview.mjs
python data.mn/scripts/validate-basketball.py
node --test data.mn/scripts/sports-browser.test.mjs
```

The browser preserves unavailable fields as null and exposes unresolved source
discrepancies. Full availability is not inferred from a box-score page.

## Public datasets

The three permanent dataset IDs are `basketball-game-results`,
`basketball-team-records`, and `basketball-player-game-stats`.
Their definitions are in `datasets/`. `build_public.py` reads the committed
`data.mn/public/sports/basketball.json` and generates the aligned EN/MN CSVs and
bilingual XLSX downloads. This build does not require the private archive.

```powershell
python tools/sources/basketball/build_public.py
python tools/sources/basketball/register.py
```

The current data produces 593 game results, 65 team-season-stage records and
9,082 player-game records, including 1,746 explicit did-not-play rows. Blank
statistics remain unavailable. Team records use game results and support the
older results-only seasons; player statistics do not exist for those seasons.

## Adding a season

Activate the repository's Python environment first. Select the new season and
stage on the public league schedule, then copy its **Mongolian** URL. The following
PowerShell commands append a new season from public pages only. The selected
schedule must contain completed games with both language reports; a fetch or
schema error stops the import. Use a fresh archive directory for a fresh pull.

```powershell
$season = Read-Host 'New season label, for example 2026-27'
$scheduleUrl = Read-Host 'Paste the selected public Mongolian league schedule URL'
$archive = "tools/sources/basketball/archive/$season"
python tools/sources/basketball/fetch_league.py --schedule-url $scheduleUrl --output $archive
if ($LASTEXITCODE -ne 0) { throw 'Resolve collection errors before continuing' }
python tools/sources/basketball/add_season.py --archive $archive --season $season --stage 'Regular season'
if ($LASTEXITCODE -ne 0) { throw 'Resolve import errors before continuing' }
python data.mn/scripts/validate-basketball.py
python tools/sources/basketball/build_public.py
python tools/sources/basketball/register.py
python tools/scripts/validate_dataset.py --all basketball-game-results
python tools/scripts/validate_dataset.py --all basketball-team-records
python tools/scripts/validate_dataset.py --all basketball-player-game-stats
```

For a first publication beginning with another stage, select that schedule and
use `--stage 'Playoffs'` or `--stage 'Play-in'`. The append command refuses an
existing season so it cannot overwrite reviewed records. Updates or additional
stages within an existing season need a reviewed reconciliation, not a blind
replacement. It preserves older seasons from the committed JSON; no old raw
images or private archive are needed. Public HTML is hashed and verified before
parsing. New team IDs are scoped to the season and the public team slug.

Review the newly added flags and coverage wording before submitting the update.
The builder updates download sizes and `dataDate`; coverage prose is reviewed
manually. Then run the global chart validation, lint and build described in
`docs/basketball-statistics-preview.md`. Permanent dataset URLs already exist;
adding a season does not create new dataset IDs or require republishing them.
