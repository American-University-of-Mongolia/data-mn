# agaar.gov.mn pull log

Per-month detail (rows, validated rows, empty stations, unavailable days) is in
`raw/agaar-pulls.json`. This file records runs and what was learned.

## 2026-10-03 to 2026-10-06: initial backfill

Everything the site served, 2025-02 → 2026-10-03, all 46 catalog stations.

| | Hourly | Daily |
|---|---|---|
| First data | 2025-06-01 | 2025-02-19 |
| Rows | 395,735 | 16,972 |
| Validated rows | 114,008 | 4,284 |
| Rows with concentrations | 281,011 | 16,972 |
| Size | ~27 MB | ~0.7 MB |

- **Coverage grows over time.** Daily 2025-02 to 2025-05 has only 1–3 aimag
  stations, 2025-06 to 2025-08 has 9–17, and the UB stations start 2025-09.
  Hourly starts 2025-06. 2025-04 has no daily rows at all.
- **Hourly concentrations are missing for validated months.** The site serves
  validated hours (2025-09, 2026-01 to 2026-07, partly) with AQI only. That
  accounts for most of the ~115k hourly rows without concentrations. Use
  daily means for those months.
- **28 station-days are unavailable.** For these the server returns an SQL
  error page every time (see SKILL.md). They are listed as `unavailable_days`
  in the manifest.
- **Some stations have little or no data.** 10702 (Өндөрхаан-02) has never
  reported. 12305 starts 2026-01, and 12306, 12404 and 12803 start 2026-09.
  11404 and 11405 report rarely.
- The first run hit a local network outage during daily 2025-03. It was
  re-run on 2026-10-06; the finished months were unaffected.

## 2026-10-06: merge fix and first `--update`

- From the PR review: `--update` used to overwrite each month's CSV, so
  NAMEM validating a month would have erased its archived hourly
  concentrations. The fetcher now merges field by field and records
  `concentrations_source`. Existing files were rewritten to add that column,
  with no values changed.
- A month now counts as complete only once it is validated (or 12 months old).
  `--update` re-fetched 2025-11, 2025-12 and 2026-08 to 2026-10. There were
  0 failures, and no file has fewer rows with concentrations than before. No
  newly validated rows appeared yet.

## Next runs

`fetch_data.py --update`, at least monthly (see source.md). Add a dated line
here when a run finds something new (catalog changes, new error patterns,
validation catching up).
