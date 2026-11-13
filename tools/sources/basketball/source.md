# Basketball source archive

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
