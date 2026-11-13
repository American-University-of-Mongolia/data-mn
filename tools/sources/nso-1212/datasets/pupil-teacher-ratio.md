# Pupils per teacher by aimag

- ID: `pupil-teacher-ratio`
- Source: Ministry of Education, published by NSO, `DT_NSO_2002_015V1.px`.
- API path: `Education, health/General educational schools/DT_NSO_2002_015V1.px`.
- Work card: https://fizzy.aum.edu.mn/1/cards/196
- Status: pending review; automatic refresh and publication disabled.
- Scope: 2007–2025; primary and all general-school levels; 21 aimags,
  Ulaanbaatar and the official national average. 874 observations per language.
- Unit: pupils per teacher, to one decimal. Do not convert to percent.

## Definition and source evidence

The bilingual JSON-stat notes define the indicator as the average number of
pupils per teacher at a given educational level in a school year. The source
web page's `%` unit conflicts with that definition. Preserve the numeric
values and label them pupils per teacher. This measures staffing ratios,
not class size, workload hours, vacancies, or teaching quality.

Independent scale check: the Ministry's 2025–2026 release reports 819,907
pupils and 39,126 full-time teachers, yielding 20.9556 pupils per teacher,
which rounds to NSO's 2025 all-level national ratio of 21.0.
https://moe.gov.mn/post/170077

Keep the NSO annual labels exactly. The 2025 match is not evidence that all
historical labels can be converted to school-year spans. The table cites
the methodology approved on 16 December 2013 (Order 01/145), but does not
document unchanged coverage and definitions across the complete history.
Do not invent a break, rebase values, interpolate, or make causal claims.

The JSON-stat `updated` field says 2007-06-04, whereas the current table
listing says 2026-05-22T15:52:53. Both are archived. Registry freshness uses
the table listing as required by the NSO source definition.

## Selection and transformation

Raw data: two indicators × 28 geographic entries × 19 years = 1,064 values
in each language. Archive the complete EN/MN metadata, exact POST queries,
JSON-stat responses and table-listing entry with SHA-256 hashes in v1/raw.

Include geography code `0` and all 22 three-digit geography codes. Omit
macroregion codes `1`, `2`, `3`, `4` and `5`. The two Ulaanbaatar codes (`5`
regional aggregate and `511` city) agree for all levels and years; assert
that before retaining only `511`. Use the official national values, never
the unweighted average of local ratios. Primary and all-level ratios are
overlapping measures with different populations; do not sum them.

Published CSVs use year, series, and pupils-per-teacher columns (localized
headers). Series combines education level and location with ` / `, a
reversible encoding of the two source dimensions. This follows the existing
one-category long-CSV/wide-XLSX download contract without changing validators.
Level display labels clarify source `Total` / `Бүгд` as `All levels` /
`Бүх түвшин`. Country `Total` / `Улсын дүн` becomes `National average` /
`Улсын дундаж`. Other labels are trimmed source labels. Raw labels remain
unchanged in the source snapshot.

Rows align by year, indicator code, then geographic code ordered by English
place name. Both language payloads must contain identical keyed numbers.
Excel uses page-language sheets with 19 year rows and 46 level/location
columns, sorted as the canonical CSV pivot expects. Each value remains a
number displayed with one decimal. Freeze the year column and header row.

## Charts

The ranking includes all 22 local areas; its dashed reference line is the
official national ratio for the selected year and education level. Colors
identify the source's geographic regions. The fixed 0–40 scale covers the
complete v1 snapshot. Years and education levels are native Vega bindings.

The trend compares two selected local areas plus the national average.
The second location can be disabled. When both selectors choose the same
location, draw it once. Stable comparison-slot colors and legend labels
avoid changing legend widths when place names change. Both charts reuse
VegaChart's existing theme, resize, and navigation lifecycle. The small
DatasetChart wrapper styles native controls and is shared with the household-income page.

## Reproduction and refresh

Run from the repository root. Use Python 3.12 and the packages in
`requirements.txt` (`requests` for fetching, `openpyxl` for Excel; the validators
also use `pandas` and `PyYAML`). For site checks, install Node 22 LTS and npm,
then use the checked-in website lockfile. Initial setup:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm --prefix data.mn ci
```

The former `build_pupil_teacher_excel.mjs` has been replaced by the shared
`build_wide_excel.py`. It needs only the public `openpyxl` dependency above;
no Codex installation, private JavaScript package, or bundled runtime is needed.
It preserves numeric values, page-language sheets, one-decimal formatting,
wrapped headers, and frozen year/header panes. Committed v1 workbooks retain
their original styling; a rebuild can change XLSX bytes without changing data.

Reproduce the existing v1 snapshot offline, in this order:

```bash
.venv/bin/python tools/scripts/build_pupil_teacher_ratio.py --version 1 --end-year 2025
.venv/bin/python tools/scripts/build_wide_excel.py pupil-teacher-ratio --input tools/temp/pupil-teacher-excel.json
.venv/bin/python tools/scripts/build_pupil_teacher_ratio.py --version 1 --end-year 2025
.venv/bin/python tools/tests/run_all_checks.py pupil-teacher-ratio
.venv/bin/python tools/scripts/validate_dataset.py --all pupil-teacher-ratio --base-dir data.mn
(cd data.mn && node scripts/test-pupil-teacher.mjs)
(cd data.mn && ../.venv/bin/python ../tools/scripts/validate_vega.py --all)
npm --prefix data.mn run check
npm --prefix data.mn run build
```

For the next release, use an unused version number and the latest **source year**,
not the year when you download it. For example, once NSO publishes 2026 data,
these are the commands for v2 through 2026 (change both flags if appropriate):

```bash
.venv/bin/python tools/scripts/fetch_pupil_teacher_ratio.py --version 2
.venv/bin/python tools/scripts/build_pupil_teacher_ratio.py --version 2 --end-year 2026
.venv/bin/python tools/scripts/build_wide_excel.py pupil-teacher-ratio --input tools/temp/pupil-teacher-excel.json
.venv/bin/python tools/scripts/build_pupil_teacher_ratio.py --version 2 --end-year 2026
.venv/bin/python tools/tests/run_all_checks.py pupil-teacher-ratio
.venv/bin/python tools/scripts/validate_dataset.py --all pupil-teacher-ratio --base-dir data.mn
(cd data.mn && node scripts/test-pupil-teacher.mjs)
(cd data.mn && ../.venv/bin/python ../tools/scripts/validate_vega.py --all)
npm --prefix data.mn run check
npm --prefix data.mn run build
```

The fetcher refuses to overwrite any raw snapshot. The builder validates source
codes, dimensions, consecutive source years and bilingual values. Stop and review
any failure; do not relax assertions to force a changed source through. The
2025–2026 Ministry comparison remains a historical methodology example.
Review changed source definitions, historical revisions, excerpts, coverage, and
these documented v1 counts before registering a new version.

Check both languages in the browser at 390px and desktop width using
`npm --prefix data.mn run dev -- --host 127.0.0.1 --port 8774`, including all
selectors, long labels, hover details and dark/light mode. Inspect the complete
Excel headers after rebuilding. Only after those checks, register the release:

```bash
.venv/bin/python tools/scripts/build_pupil_teacher_ratio.py --version 2 --end-year 2026 --register
```

For the initial v1 registration, the equivalent final command is:

```bash
.venv/bin/python tools/scripts/build_pupil_teacher_ratio.py --version 1 --end-year 2025 --register
```

Registration is repeatable and does not publish the dataset. Maintainers run
`(cd tools && ../.venv/bin/python -m registry publish pupil-teacher-ratio)` at
merge time. Start registry edits from current main so unrelated rows survive.
