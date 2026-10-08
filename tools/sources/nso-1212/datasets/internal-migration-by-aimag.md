# Internal migration by aimag

- ID: `internal-migration-by-aimag`
- Source: NSO 1212.mn, `DT_NSO_0300_040V1.px`, annual internal migration report XA-2.
- API path: `Population, household/1_Population, household/DT_NSO_0300_040V1.px`
- Coverage: 1983–2025; 21 aimags and Ulaanbaatar; people, annual frequency.
- Status: pending review, not published; automatic updates/publication disabled.
- Work card: https://fizzy.aum.edu.mn/1/cards/189

## Meaning and selection

The source reports recorded arrivals and departures within Mongolia. It does
not measure total population change, unique lifetime movers, reasons for moving,
or origin–destination pairs. Net migration is derived as arrivals minus
departures; positive means more recorded arrivals than departures.

Select the 22 three-digit region codes. Exclude national and macroregion totals
and the duplicate one-digit Ulaanbaatar aggregate to avoid double counting.
Year codes are positional: map them through metadata labels. Both language
responses contain 2,408 cells. The 946 place-year observations contain 1,892
source measure values and 946 derived net values. The builder checks EN/MN
parity, unique keys, nonnegative source counts, every year, and the provincial
sums against the national total for each source measure and year.

## Comparability limits

National arrivals and departures do not balance before 2020. Their equality in
2020–2025 does not prove complete comparability. Govisumber (342) has source
zeros in 1983–1990; do not interpret those as confirmed absence of movement.
No discrepancies or zeros are silently corrected. The charts include all
1983–2025 values at the contributor's request and show a visible historical
caution. Current `mongolia-aimags.json` geometry is used for every year; this is
not a reconstruction of historical administrative boundaries. Counts are not
population-adjusted. Avoid causal conclusions or treating net counts as rates.

## Downloads and charts

- Chart CSV: 946 rows; year, region, incoming, outgoing, net, with translated
  headers and place names in the Mongolian file.
- Download CSV: 2,838 rows; year, aimag/measure category, people. Each category
  joins the place name and measure label using ` — `; this preserves all three
  measures while fitting the canonical single-value long-form download contract.
- Excel: one page-language sheet (`English` or `Монгол`), 43 time rows and 66
  place/measure columns, built by `rebuild_downloads.py`. No rows are omitted.
- Map: fixed symmetric color domain over the full history, year slider and
  tooltips. Ranking follows the map's year. Trend selects one place and shows
  all 43 years. CSV/Excel contents are independent of UI selections.

## Reproduction and refresh

```bash
python tools/scripts/build_internal_migration.py
# Register the pending dataset/version once; does not publish.
python tools/scripts/build_internal_migration.py --register
python tools/tests/run_all_checks.py internal-migration-by-aimag
python tools/scripts/validate_dataset.py --all internal-migration-by-aimag --base-dir data.mn
cd data.mn && npm run build && npm run check
```

The offline builder verifies SHA-256 hashes of both metadata, queries and data
responses in `tools/versions/internal-migration-by-aimag/v1/raw/manifest.json`.
The snapshot was fetched on 6 October 2026 UTC. The source response's own update
timestamp is `2025-04-12T00:00:00Z`; retain that literal value separately from the
retrieval date and latest observation year, rather than infer a newer timestamp.

For a refresh, preserve v1. Fetch metadata from the API path above in both
languages, then POST the complete per-language query recorded in `raw/query-*.json`
(response format `json`). Review added years, region codes, method notes and
national balances, archive the new responses and hashes in a new version, and
update the builder's version/coverage assertions only after review. Source page:
https://data.1212.mn/pxweb/en/NSO/NSO__Population%2C%20household__1_Population%2C%20household/DT_NSO_0300_040V1.px/
