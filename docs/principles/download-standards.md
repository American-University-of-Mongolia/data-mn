# Download Standards (Standard 1 + Standard 2)

Every data.mn dataset page offers downloads. These two standards keep them
consistent. Enforced by `tools/scripts/validate_dataset.py`
(4 download-standards checks; `--all` must show `Valid: 15, Invalid: 0`).

Canonical builder: `tools/scripts/rebuild_downloads.py`
(`--dataset {id} --apply`, or `--all --apply`). All creation and refresh
pipelines must produce output this script would also produce — or call it.

## Standard 1: Two bilingual files

Each dataset has exactly these downloads:

| File | Content |
|------|---------|
| `{id}-all-{lang}.csv` (or `{id}-{lang}.csv` when no chart subset exists) | ALL data, long form |
| `{id}.xlsx` | ALL data, wide form, bilingual workbook |

Rules:

1. **Exactly 2 files** in MDX `dataFiles` (one CSV + one XLSX). By default the
   workbook is bilingual. Explicit page-language exports are described below.
2. **Default XLSX sheets**: `English` first, `Монгол` second. Freeze top row,
   auto-size columns.
3. **EN and MN content equivalent**: same rows/values, only labels differ.
4. **MN page fully Mongolian**: excerpt, title, tags, `description` strings
   (`CSV татах (бүх өгөгдөл)`, `Excel татах`). EN page fully English.
5. **Chart CSVs are not downloads**: `{id}-{lang}.csv` chart subsets (4–6
   categories for readability) are referenced only by the chart spec, never
   in `dataFiles`. Downloads always contain ALL data.
6. **No Latin value translation beyond headers**: structural column headers
   are translated (EN sheet English headers, MN sheet Mongolian headers),
   but cell values stay as-is — Latin unit codes (MNT, USD) and proper names
   are conventionally Latin and must not be transliterated.
7. **Boundary downloads**: boundary datasets list the GeoJSON shapes file
   instead of the CSV (`{maps-file}.json` + `{id}.xlsx` — still exactly 2
   files). The CSVs are still built (chart data and XLSX source) but not
   listed. Listed ids live in `BOUNDARY_SHAPES` in `rebuild_downloads.py`;
   the validator shares the list.

### Optional page-language Excel downloads

Set `excelLanguage: page` on both EN and MN pages to offer `{id}-en.xlsx`
with only the `English` sheet and `{id}-mn.xlsx` with only the `Монгол` sheet.
Each page still lists exactly two downloads: its CSV and its Excel file.
Both workbooks contain equivalent data and the full available history.
The builder and validator require the two pages to agree on this setting and
check matching filenames and sheet languages. Existing bilingual URLs may
remain available for earlier links, but are not offered by these pages.

The three livestock-loss datasets use this mode at the contributor's request,
so changing the page language also changes the Excel download language.
Datasets without this setting retain the default bilingual workbook.

## Standard 2: Long CSV, wide XLSX

1. **CSV is long/tidy**: one observation per row
   (`date,region,price`). Never pivoted.
2. **XLSX is wide/pivoted**: rows = time, columns = categories, values = data.
   A wide sheet that is merely a copy of the long CSV fails validation.
3. **Pivots must actually be transposed**: time dimension down the rows,
   category dimension across the columns. Single-series time data (no
   category column) is trivially wide and passes as-is.
4. **Cross-sectional exemption**: datasets with no time dimension
   (single-year snapshots, cross-sectional counts) are exempt from the wide
   rule but still get bilingual sheets. Exempt ids live in `EXEMPT_WIDE` in
   `rebuild_downloads.py` with a documented reason each; adding a new one
   requires a reason string there. The validator shares the same list.
   Current exemptions: `gdp-by-sector`, `health-facilities-by-aimag`,
   `health-facilities-by-type`, `hospital-beds-by-type`,
   `population-pyramid-mongolia`, `salary-by-sector-2024`.
5. **Reference-table exemption**: boundary lists and codebooks are timeless
   and multi-attribute (codes, names, parents, areas, coordinates), so the
   single-value-column rule cannot apply. Listed ids live in
   `REFERENCE_TABLES` in `rebuild_downloads.py` with a reason each;
   structural = text columns only (numeric headers such as `lon`/`lat`
   are conventionally Latin in both languages). Sheets stay long and must
   match their CSV shape exactly. The validator shares the same list.

## Related

- Explorer year-less guard (`VegaChart.astro` `hasYears` branch): exempt /
  year-less datasets render a no-years grid instead of year controls.
- Skills: `datamn-transform-split` (exports), `datamn-page-mdx` (dataFiles).
- URL stability for renames: `docs/principles/url-stability.md`.
