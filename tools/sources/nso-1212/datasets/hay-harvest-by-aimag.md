# hay-harvest-by-aimag

**Source:** National Statistics Office of Mongolia, 1212.mn
**Source table:** `DT_NSO_1002_007V1.px` ("GROSS HAY HARVEST AND LAYING-IN OF FODDER, by aimags and the Capital, and by year")
**Category:** Agriculture / Хөдөө аж ахуй
**Frequency:** Annual, 1960–2025 (source updated 2026-01-15)
**Retrieved:** 2026-11-05
**Measure:** Hay cut and fodder laid in for winter, **thousand tonnes**. Unit confirmed from the json-stat2 response (`unit.EliminatedValue.base` = "thousand tonnes" in EN, "мян.тн" in MN); the table title and variable metadata do not state it.
**Source note:** Hay harvest of households and enterprises (survey A-ХАА-9; methodology: NSO order A/188, 2022-11-07).

## Access

```text
GET/POST https://data.1212.mn/api/v1/{en,mn}/NSO/Industry,%20service/Agriculture/DT_NSO_1002_007V1.px
```

Query: every `Бүс` (region) code and every `он` (year) code, `response.format = json-stat2`. Bodies, metadata and responses are saved in `tools/versions/hay-harvest-by-aimag/v1/raw/`; `manifest.json` holds hashes.

## Selection

- Region codes: 22 leaves (21 aimags plus Ulaanbaatar, code `511`). Excluded: national total (`0`), five regional groups (`1`–`4`, and capital group `5`, which duplicates `511`).
- Years 1960–2025 (66). Region labels carry leading whitespace; trimmed.
- English labels match `public/maps/mongolia-aimags.json` `name`; Mongolian labels match `name_mn`.

## Missing values

63 of 1,452 leaf cells are source `..` and are left empty in the CSV and XLSX (never zero): Govisumber before 1991, Orkhon before 1977, Darkhan-Uul 1960–62, and Ulaanbaatar in 1960 and some later years including 2017. Maps show them grey. The 22-unit sum differs from the national total in some years (largest in 2017, 28 thousand tonnes, where Ulaanbaatar is blank); 2025 leaf sum 1,809.50 vs total 1,809.49 (rounding).

## Outputs

CSV `year,region,value` / `он,бүс,утга`, 1,452 rows per language, rows aligned by source code. Charts: choropleth with year slider plus top-six ranking sharing the slider (`yearGroup`). Colour bounds fixed to the full-series maximum. Pages use `excelLanguage: page` (single-sheet XLSX per language, built by `tools/scripts/rebuild_downloads.py`).

## Reproduction

```bash
python3 tools/scripts/build_hay_harvest_by_aimag.py   # CSVs + charts from saved raw
python3 tools/scripts/rebuild_downloads.py --dataset hay-harvest-by-aimag --apply
```

Related: `hay-prices-by-region`, `livestock-losses-by-aimag`.
