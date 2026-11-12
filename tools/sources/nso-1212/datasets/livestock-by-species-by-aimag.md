# livestock-by-species-by-aimag

**Parent:** `nso-livestock-by-aimag`
**Source table:** `DT_NSO_1001_109V1.px`
**Selection:** `region_level = aimag` (21 aimags plus Ulaanbaatar city; the Ulaanbaatar regional group is excluded), `livestock_type` in Horse, Cattle, Camel, Sheep, Goat (Total excluded), annual 1970–2025.
**Measure:** Number of livestock, thousand head.
**CSV:** one file per language, used by both the page download and the chart: `year,category,value` / `он,ангилал,утга`, category = "{Region} — {Species}" (e.g. "Arkhangai — Horse" / "Архангай — Адуу"); the chart splits it back into region and species. 6,160 rows per language (22 units x 5 species x 56 years), row-aligned EN/MN. Blank = missing, never 0; the genuine camel zero stays 0. XLSX: `livestock-by-species-by-aimag-en.xlsx` / `livestock-by-species-by-aimag-mn.xlsx` (excelLanguage: page), built by `rebuild_downloads.py`.
**Chart:** Stacked horizontal bar per aimag, sorted by total, coloured by species (Horse #4c78a8, Cattle #f58518, Camel #e45756, Sheep #72b7b2, Goat #54a24b, as in `livestock-by-type`), controlled by a 1970–2025 year slider (default 2025).
**Downloads:** Long-format CSV per language and a wide XLSX (year, region, one column per species).
**Known gaps:** Govisumber 1970–1990; Orkhon 1970–1975 (camel to 1991); Darkhan-Uul camel 1970–1988; Ulaanbaatar camel 1970–1978.

See [parent definition](nso-livestock-by-aimag.md) for source endpoints, definitions, exclusions and quirks.
