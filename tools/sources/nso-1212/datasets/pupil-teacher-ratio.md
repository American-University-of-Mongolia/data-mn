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
PupilTeacherChart wrapper styles only this dataset's native controls.

## Reproduction

```bash
# Offline, hash-verified build; emits CSVs, charts, pages and wide JSON.
python tools/scripts/build_pupil_teacher_ratio.py
# Generate Excel with @oai/artifact-tool available to Node.
node tools/scripts/build_pupil_teacher_excel.mjs
# Refresh download sizes in MDX after Excel export.
python tools/scripts/build_pupil_teacher_ratio.py
# Add pending registry entry and version once, without publishing.
python tools/scripts/build_pupil_teacher_ratio.py --register
python tools/tests/run_all_checks.py pupil-teacher-ratio
python tools/scripts/validate_dataset.py --all pupil-teacher-ratio --base-dir data.mn
cd data.mn
node scripts/test-pupil-teacher.mjs
npm run check
npm run build
```

`fetch_pupil_teacher_ratio.py` creates the first immutable snapshot and
refuses to overwrite an existing one. For a refresh, archive a new version,
re-read dimension codes and definitions, review changed years and values,
and update the builder's explicit coverage assertions. Never assume that
year-code `0` still means 2025. Verify all four chart specs and both language
pages at desktop and mobile widths, including theme and control changes.
