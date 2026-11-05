# Basketball source archive

The preview uses supplied FIBA reports and public Mongolian Basketball
Association pages. Koo archives preserve older season results. These are
preview inputs, not newly published registry datasets.

## Files retained in Git

- `archive-manifest.json`: 718 paths, lengths, SHA-256 hashes and proposed
  MinIO object keys. Storage status is **pending-upload**.
- `archive-package.json`: ZIP filename, length and SHA-256.
- `league-pages-manifest.json`: original URLs, UTC retrieval times and hashes
  for 276 saved schedule/game pages (135 games in each language).
- `game-id-mapping.json`: reviewed website-to-MBA IDs, checked against date
  and team order during import.
- `conflicting-score-play-by-play.json`: final events used in score review,
  auditable against the original saved HTML.
- `regular-season-reconciliation.json`: all 270 team-game score comparisons.
- `regular-season-validation.json`: generated import counts.

## Storage status

Documented endpoint: `https://s3.data.mn`; bucket: `data.mn`.
Proposed new prefix: `basketball/pr-183/2026-11-03/`.

The endpoint fails TLS negotiation from this workstation. No upload or public
access has been verified and no bucket policy was changed. The author holds
a verified external backup and the ZIP named in `archive-package.json`.
Proposed object keys are not live URLs.

Once the approved endpoint is reachable, configure credentials through the
standard AWS environment/profile mechanism and run:

```sh
python tools/sources/basketball/upload_archive.py /path/to/restored/archive --endpoint https://s3.data.mn --bucket data.mn --receipt /path/to/upload-receipt.json
```

The uploader refuses to overwrite a different object and downloads each
uploaded object to verify SHA-256. It does not alter ACLs or bucket policy.
Only after verifying the receipt should storage status and download locations
be updated. Never commit credentials or temporary signed URLs.

## Restore and rebuild

`restore_archive.py ARCHIVE.zip DESTINATION` checks the ZIP and every file
against the committed manifest. Use an empty destination; differing existing
files are never overwritten. Follow the commands in
[the preview guide](../../../docs/basketball-statistics-preview.md).

For a fresh public collection, set `BASKETBALL_WEB_ARCHIVE` to a new directory
and run `python tools/sources/basketball/fetch_league.py`. It follows the
schedule's month and game links, waits at least 0.8 seconds between requests,
and archives both languages with hashes. Existing pages are reused only after
hash verification. Fresh source changes require renewed reconciliation; the
reviewed mapping and score decisions must not be assumed valid for a different
season. Copy the committed game mapping and play-by-play audit into a reviewed
archive before running the importer, after checking them against its pages.

The browser preserves unavailable fields as null and exposes unresolved
source discrepancies. Full availability is not inferred from a box-score page.
