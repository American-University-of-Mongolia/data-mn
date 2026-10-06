# National real-wage index review draft

## Scope

One national dataset, `real-wage-index-national`, with all 34 annual observations for 1992–2025 from NSO table `DT_NSO_0400_036V4.px` (2023 = 100). The EN/MN values and immutable v1 source snapshots are unchanged from the 30 September 2026 checkpoint.

Includes bilingual pages, charts, CSV downloads, page-language Excel downloads, thumbnails, a reproducible builder, and one pending registry dataset/version. The original bilingual workbook is retained for the existing demo path. No shared components or existing datasets are modified. Publication, auto-publication, and automatic refresh remain off.

Tracking: [Fizzy card #187](https://fizzy.aum.edu.mn/1/cards/187).

## Decision requested from Robert

The draft retains the full official history, solid segments for 1992–2013 and 2014–2024, dashed connectors across the boundaries, and an orange 2025 point.

- **2014:** a documented switch from the establishment survey to Social Insurance Fund data. Comparability/harmonization across this boundary has not been confirmed; this is not an explicit NSO statement of non-comparability.
- **2025:** NSO explicitly says the revised methodology is not comparable with earlier years.

Should the contribution keep this full-history presentation with clear warnings, use a shorter period, or await NSO clarification? No statistical bridge, imputation, or source-value adjustment has been made. The page wording distinguishes the two strengths of evidence.

## Registration

`Registry.add_dataset` persists only core metadata; file paths, dates, and coverage are saved explicitly through `update_dataset`. Rerunning against the matching pending v1 repairs metadata without adding duplicate versions or activity. Changed, newer, published, or automatically managed records are rejected. Only the new wage dataset, version, and activity rows are added to the current upstream registry; the archived database is not copied over it.

The saved API response reports a source update date of 21 April 2026; snapshot retrieval was 30 September 2026. Registration preserves that distinction. Canonical URL and publication fields remain unset until the maintainer's publication workflow.

## Validation — 6 October 2026

- Source hashes and unchanged raw/derived v1 files verified; 34 consecutive years, EN/MN parity, no missing values, and 2023 = 100.
- Both page-language workbooks checked cell by cell against their CSVs; matching sheet language, 34 data rows, frozen headers/year column, and table filters.
- Unified dataset checks: 51/51 passed. Comprehensive file checks: 19/19 valid (current validator includes title-year and claim checks).
- All chart specifications valid; all 356 MDX download references valid; scoped deprecation check passed.
- Nine regression tests pass, covering source preservation, additive registration, metadata repair, and refusal to overwrite changed/active records.
- Full production build passed. Astro check: 0 errors, 0 warnings.
- EN/MN desktop and mobile pages visually inspected; language switching, matching download links, and no horizontal overflow on mobile verified. Browser error log was empty.
- Repository-wide `npm run check` fails at ESLint: 643 existing errors across 20 files. A clean worktree of upstream `d3c21d4` has identical diagnostics. The separately run Prettier check also fails on upstream; its diagnostics are unchanged. The wage MDX/JSON files pass their scoped formatting check. These baseline failures need maintainer acceptance; this draft is not a claim that all repository gates are green.

## Reproduce

From the repository root with the project's Python dependencies installed:

```bash
python tools/scripts/build_real_wage_index.py
python tools/scripts/rebuild_downloads.py --dataset real-wage-index-national --apply
python tools/scripts/register_real_wage_index.py
python -m pytest tools/tests/test_real_wage_index.py -q
python tools/tests/run_all_checks.py real-wage-index-national
python tools/scripts/validate_dataset.py --all real-wage-index-national
cd data.mn
npx prettier --write public/charts/real-wage-index-national-*.json src/data/data/{en,mn}/real-wage-index-national.mdx
npm run build
npm run check
```

Default builds are offline from the saved snapshot. Do not use `--fetch` to refresh v1; new data requires a separately reviewed version. The older offline demo remains a checkpoint artifact; it predates these wording and page-language download corrections.
