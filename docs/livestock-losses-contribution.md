# Livestock losses: contribution for review

Updated 22 September 2026 against `origin/main` commit `309ce45`. The combined preview is on `add/livestock-losses`; the review branches below separate the three page datasets.

## Why this data

The Data.mn catalog checked for this task already covered livestock stocks, but no equivalent adult-livestock-loss or regional loss-rate datasets were found. This contribution lets readers compare the number of animals lost and the share of the starting herd lost. Those measures answer different questions: a large herd can have a large count without the highest proportional loss.

The draft now covers all available years, 1971–2025 (55 years). It uses official NSO loss and year-end-herd tables, retrieved in both languages. Rates are calculated by Data.mn. Losses include several causes and must not be attributed exclusively to dzud. The original 2010–2025 extract is preserved as version 1; overlapping observations are unchanged in version 2.

| Dataset | Scope | Rows in each CSV | Unit |
|---|---|---:|---|
| `livestock-losses-by-aimag` | 21 aimags + Ulaanbaatar | 1,210 | Thousand head |
| `livestock-loss-rate-by-aimag` | 21 aimags + Ulaanbaatar | 1,210 | Percent of previous year-end herd |
| `livestock-losses-by-type` | National, five animal types | 275 | Thousand head |

Each dataset includes English and Mongolian pages and CSVs, separate English and Mongolian Excel workbooks, chart specifications and thumbnails. Regional pages provide a map and a top-six ranking that update together using one 1971–2025 year slider (default 2025). Downloads retain all 22 region labels and historical blanks. The animal-type chart shows all five types across the full period, with matching colors in both languages.

Orkhon loss records start in 1976 and Govisumber records in 1991. The regional downloads contain 25 unavailable loss counts and 30 unavailable rates, kept blank rather than converted to zero. Five additional rates lack a previous-year herd. Historical administrative boundaries changed; regional series follow the source's labels. Both points are explained on the pages and in the source definition.

Five historical years have national animal-type sums that differ from the separately reported total by more than the one-decimal rounding tolerance: 1996, 1997, 1998, 1999, and 2005. Both language responses agree. These source discrepancies (at most 0.7 thousand head) are documented and preserved.

For context, the source reports 9,364.083 thousand losses nationally in 2024 and 358.942 thousand in 2025. Sukhbaatar's calculated 2024 rate is 47.286092%: 1,824.993 thousand losses divided by 3,859.471 thousand animals at the end of 2023, multiplied by 100. These are source-based counts and a derived rate, not a causal estimate.

Sources: [NSO adult livestock losses](https://data.1212.mn/pxweb/en/NSO/NSO__Industry,%20service__Livestock/DT_NSO_1001_029V1.px/), [NSO livestock numbers](https://data.1212.mn/pxweb/en/NSO/NSO__Industry,%20service__Livestock/DT_NSO_1001_021V1.px/). Full methodology and reproduction steps are in [the parent definition](../tools/sources/nso-1212/datasets/nso-livestock-losses.md).

## Validation

| Check | Result |
|---|---|
| Unified dataset checks | 150/150 pass: 49 + 49 + 52 |
| Comprehensive dataset validator | 15/15 pass for each of the three datasets |
| Vega specification validation | All 10 chart specifications pass |
| Runtime chart checks | All 22 map shapes and values checked for all 55 years; missing values stay grey; all rankings match; linked year/heading updates, delayed loading, rapid input and resize tested with the site’s Vega 5.30.0 runtime |
| Bilingual parity | Every exported numeric row matches across languages |
| Excel parity | Every data cell matches its CSV pivot; one correctly named sheet per language file, frozen headers, no formula errors |
| Source controls | All 7,590 joined observations checked; hashes verified; every rate recomputed; national totals reconcile to available regional totals within 0.2 thousand head; five historical type-total discrepancies documented |
| Missing data | 314 missing source loss values and 207 missing herd values preserved; exported counts/rates retain 25/30 blanks; national animal-type series are complete |
| MDX download paths | Global check passes for all 336 pages |
| Download contract | Canonical rebuild preserves page-language filenames for all three datasets |
| Validator regressions | 23 tests pass, including page-language download and rebuild regressions |
| Site build | Updated dataset pages render successfully. The full rebuild was blocked by automatic approval review of an unrelated demo tweet embed request to publish.x.com; the local preview retains the prior build for unchanged remaining pages. |
| New JSON/MDX formatting | Prettier passes on all new chart/page files |
| Repository-wide `npm run check` | Astro: 0 errors, 0 warnings. Baseline has 53 existing lint errors; changed-file comparisons show no additional errors (chart component 24 → 24; dataset page 5 → 5; schema and both new runtime tests 0 → 0). |

The six page-language Excel downloads retain consistent styling and number formats for every year (1971–2025), with one filterable table and a frozen header/year column in each workbook. Every cell and historical blank matches the corresponding language sheet of the preceding bilingual workbooks. English pages download only the English workbook; Mongolian pages download only the Mongolian workbook. Both pages set `excelLanguage: page`, and rebuilds preserve that choice. The older bilingual paths remain available for previous links. The six updated download sections were rendered through the local Astro development server, their download responses were checked against the files, and they are included in the portable preview.

Chart PNGs were inspected. Runtime chart tests caught and corrected a CSV byte-order-mark issue before packaging. Existing global lint problems were left outside this contribution.

Two stale unified-check assumptions were corrected: choropleth language checking now inspects the lookup CSV rather than the shared geometry filename, and the workbook check follows the current standard of time down rows and categories across columns. Regression tests also reject a wrong-language lookup, a hidden wrong-language layer, long-form spreadsheet copies and transposed legacy layouts. The colour-domain checks now distinguish numeric scale endpoints from categorical labels; regression tests retain wrong-language/category detection. The new maps load the full language-specific CSV and join shared geometry, so the previous geometry-filename warnings no longer apply.

## Review and publication status

This is a local, reviewable contribution. No pull request, merge, deployment or Campfire message has been made at preparation time. Fizzy idea card [#153](https://fizzy.aum.edu.mn/1/cards/153) tracks this contribution. The combined registry contains one source parent and three pending page datasets at version 2, with the original version 1 records preserved. Automatic refresh/publication and published-URL flags are disabled.

Relative to the baseline, the registry diff adds four datasets, eight version records and eight activity records. It changes no pre-existing baseline records. The version-2 registration script updates the four pending draft records and appends history without overwriting version 1; rerunning it with the same data makes no further changes.

The internship guide asks for one dataset per pull request. The review branches form a stack:

1. `add/livestock-losses-by-aimag` → `main`: regional counts plus shared source, download, chart and validator support; registers only the source parent and this page dataset.
2. `add/livestock-loss-rate-by-aimag` → `add/livestock-losses-by-aimag`: adds regional rates and their registry history.
3. `add/livestock-losses-by-type` → `add/livestock-loss-rate-by-aimag`: adds national animal-type losses and their registry history.

Review and merge in that order, updating each later branch onto the merged predecessor before retargeting it to `main`. This avoids independent changes to the binary registry. The registration script only registers child datasets whose pages are present. Runtime checks likewise exercise the regional pages present on each branch.

Publication is pending GitHub access and the repository's full validation gate. The blocked build and existing global lint failures above must be resolved or explicitly accepted by maintainers; these branches must not be represented as merge-ready. The repository's `AGENTS.md` requires Robert's confirmation before merge and deployment. Before first deployment, register the three canonical URLs with `registry publish` and set the datasets active after review. The custom two-table refresh remains manual until its update workflow is reviewed.

To run focused checks:

```bash
python3 -m pytest tools/tests/test_current_download_and_map_checks.py tools/tests/test_page_language_excel.py -q
python3 tools/tests/run_all_checks.py livestock-losses-by-aimag
python3 tools/tests/run_all_checks.py livestock-loss-rate-by-aimag
python3 tools/tests/run_all_checks.py livestock-losses-by-type
python3 tools/scripts/validate_dataset.py --all livestock-losses-by-aimag --base-dir data.mn
python3 tools/scripts/validate_dataset.py --all livestock-loss-rate-by-aimag --base-dir data.mn
python3 tools/scripts/validate_dataset.py --all livestock-losses-by-type --base-dir data.mn
python3 tools/scripts/validate_mdx_datafiles.py
cd data.mn
node scripts/test-linked-chart-years.mjs
node scripts/test-livestock-maps.mjs
npm run build
npm run check
```
