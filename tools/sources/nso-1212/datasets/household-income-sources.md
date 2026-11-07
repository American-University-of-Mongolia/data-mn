# Household income sources, 2007–2025

Local demo for Fizzy card https://fizzy.aum.edu.mn/1/cards/200.

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
The selected 2007 start is the demo's scope, not a claimed methodology break.
The source table does not provide uncertainty intervals or a full survey
comparability history; do not infer causation or precise changes in household
behavior from the composition series alone.

Rebuild with `build_household_income_sources.py`, then
`build_household_income_excel.mjs`, then the Python builder again to update
download sizes. The Excel builder uses the bundled artifact-tool runtime.
Fetcher refuses to overwrite snapshots. No registry entry or publication is
performed for this local demo.
