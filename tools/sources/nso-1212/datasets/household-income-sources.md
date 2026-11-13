# Household income sources, 2007–2025

Dataset tracked by Fizzy card https://fizzy.aum.edu.mn/1/cards/200.

- ID: `household-income-sources`
- Source: NSO Household Socio-Economic Survey
- Table: `DT_NSO_1900_003V1.px`
- API path: `Society, development/Household income and expenditure/DT_NSO_1900_003V1.px`
- Unit: percent, stored on a 0–100 scale
- Source updated: 2026-05-29
- Scope: 2007–2025, national average/urban/rural, eight official series
- Pages/downloads: English and Mongolian; page-language Excel

The six non-overlapping components are source codes 2–7. Codes 0 and 1 are
total income and monetary income: included in full downloads but excluded
from chart stacks. National values are official estimates, not averages of
the urban and rural percentages. Every 2007–2025 location/year reconciles
to 100%; the first four components reconcile to monetary income.

Both language responses, metadata, exact queries, listing timestamp and
SHA-256 hashes are archived in `tools/versions/household-income-sources/v1/raw`.
Match languages by source codes, never translated sort order. All 456
published observations per language use the same row ordering. The raw
archive retains the entire 1997–2025 source, including early missing values.
The selected 2007 start is the page's scope, not a claimed methodology break.
The source table does not provide uncertainty intervals or a full survey
comparability history; do not infer causation or precise changes in household
behavior from the composition series alone.

## Shared chart presentation

Both pages use `DatasetChart.astro`, introduced in PR #181 and shared with
pupil–teacher ratios. The income page imports its stacked chart JSON and passes
that same spec's colour-scale domain/range to the HTML legend. There is no
separate hardcoded palette in the wrapper or MDX. Long labels wrap at phone width.

## Reproduction and refresh

Run commands from the repository root with Python 3.12. Install the repository
requirements (`requests` for fetching; `openpyxl` for Excel; `pandas` and
`PyYAML` for validators). Install Node 22 LTS and npm for website checks:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm --prefix data.mn ci
```

`build_household_income_excel.mjs` has been replaced by the shared
`build_wide_excel.py`. Excel generation requires only public `openpyxl`, already
in `requirements.txt`; it does not need Codex, `@oai/artifact-tool`, or a bundled
runtime. Existing v1 downloads retain their original styling. Rebuilding can
change XLSX bytes while retaining all values and the wide, page-language format.

Reproduce v1 offline from the archived source, in this order:

```bash
.venv/bin/python tools/scripts/build_household_income_sources.py --version 1 --end-year 2025
.venv/bin/python tools/scripts/build_wide_excel.py household-income-sources --input tools/temp/household-income-excel.json
.venv/bin/python tools/scripts/build_household_income_sources.py --version 1 --end-year 2025
.venv/bin/python tools/tests/run_all_checks.py household-income-sources
.venv/bin/python tools/scripts/validate_dataset.py --all household-income-sources --base-dir data.mn
(cd data.mn && node scripts/test-household-income.mjs)
(cd data.mn && ../.venv/bin/python ../tools/scripts/validate_vega.py --all)
npm --prefix data.mn run check
npm --prefix data.mn run build
```

For a future release, choose an unused snapshot version and the latest source
year. For example, after NSO releases 2026 data, the v2 refresh is:

```bash
.venv/bin/python tools/scripts/fetch_household_income_sources.py --version 2
.venv/bin/python tools/scripts/build_household_income_sources.py --version 2 --end-year 2026
.venv/bin/python tools/scripts/build_wide_excel.py household-income-sources --input tools/temp/household-income-excel.json
.venv/bin/python tools/scripts/build_household_income_sources.py --version 2 --end-year 2026
.venv/bin/python tools/tests/run_all_checks.py household-income-sources
.venv/bin/python tools/scripts/validate_dataset.py --all household-income-sources --base-dir data.mn
(cd data.mn && node scripts/test-household-income.mjs)
(cd data.mn && ../.venv/bin/python ../tools/scripts/validate_vega.py --all)
npm --prefix data.mn run check
npm --prefix data.mn run build
```

The fetcher refuses to overwrite any raw snapshot. The builder verifies source
hashes, dimension codes, complete selected years, bilingual parity, six-component
100% totals, and monetary subtotals. Stop on failures and review methodology and
historical revisions; do not loosen assertions simply to get a build. Update
this definition's coverage/counts and inspect the derived latest-year claims.

Use `npm --prefix data.mn run dev -- --host 127.0.0.1 --port 8776` to inspect both
languages at 390px and desktop width. Test year/source/location selection,
legend wrapping, tooltips and dark/light mode. Check the Excel headers too.

## Registry ordering

PR #185 and its publication follow-up #188 have merged. **Wait for #181 to merge
and be published**, then merge main into this branch and use main's registry.
The shared wrapper and Excel builder should then come from #181. Register v1:

```bash
git fetch upstream main
git merge upstream/main
.venv/bin/python tools/scripts/build_household_income_sources.py --version 1 --end-year 2025 --register
```

After validating a later refresh, use its matching flags for registration:

```bash
.venv/bin/python tools/scripts/build_household_income_sources.py --version 2 --end-year 2026 --register
```

Registration is repeatable, adds the dataset/version, and does not publish.
Automatic refresh/publication remain disabled. The initial registration guard
requires the published pupil–teacher dataset so these binary database edits
cannot accidentally be applied before #181. Maintainers will run
`(cd tools && ../.venv/bin/python -m registry publish household-income-sources)`
at merge time. No production deployment is part of the builder.
