# Dataset: Apartment Prices Ulaanbaatar

## Identification

- **ID**: `apartment-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [apartment, housing, real-estate, ulaanbaatar, prices]

## Source Reference

- **Table ID**: `DT_NSO_0300_00V4.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Housing price index`
- **Last Updated**: 2026-01-12

## Title

- **EN**: Ulaanbaatar Apartment Prices per sqm, New vs Old, Monthly (2022-2026)
- **MN**: Улаанбаатарын орон сууцны м.кв-ын дундаж үнэ, шинэ ба хуучин, сар бүр (2022-2026)

## Description

Monthly average apartment price per square meter in Ulaanbaatar, based on the 6 central districts (Bayangol, Bayanzurkh, Songinokhairkhan, Sukhbaatar, Khan-Uul, Chingeltei). This dataset uses the "Average" / "Дундаж" row which is the city-wide average across all 6 districts. Two indicators: new apartment and old apartment prices.

## Variables

### Indicator (Үзүүлэлт)
- `Average price of new apartment` / `Шинэ орон сууцны дундаж үнэ`
- `Average price of old apartment` / `Хуучин орон сууцны дундаж үнэ`

### District (Дүүрэг)
Source table has 7 entries (6 districts + Average). This dataset uses only "Average" / "Дундаж".

Available districts (for future splits):
- Bayangol / Баянгол
- Bayanzurkh / Баянзүрх
- Songinokhairkhan / Сонгинохайрхан
- Sukhbaatar / Сүхбаатар
- Khan-Uul / Хан-Уул
- Chingeltei / Чингэлтэй

### Month (Сар)
49 months: 2022-02 to 2026-02

## Update Instructions

Query the API for table `DT_NSO_0300_00V4.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0300_00V4.px --output ./output
```

Filter: District="Average" for city-wide average.

## Notes

- Values are in million MNT per square meter
- City-wide average only — no district-level splits in this dataset
- New apartment prices are slightly higher than old apartment prices
- Both series show strong upward trend: ~3.0 million MNT/sqm (early 2022) to ~5.0 million MNT/sqm (late 2025)
- Related tables: DT_NSO_0300_00V1.px (annual price change %), DT_NSO_0300_071V0.px (housing price index)
