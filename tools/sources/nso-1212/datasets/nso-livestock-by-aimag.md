# nso-livestock-by-aimag

**Source:** National Statistics Office of Mongolia, 1212.mn
**Category:** Agriculture / Хөдөө аж ахуй
**Frequency:** Annual
**Coverage:** 1970–2025, national total, 6 regional groups, Ulaanbaatar group, 21 aimags and Ulaanbaatar city
**Retrieved:** 2026-11-05
**Role:** Parent (raw data only; no MDX page or chart)

## Official table

| Table | Path | Last source update | Unit |
|---|---|---|---|
| `DT_NSO_1001_109V1.px` | `Regional development/Livestock` | 2026-07-21T17:37:54 | Thousand head |

Title: "NUMBER OF LIVESTOCK, by type of livestock, aimags and the Capital, and by year". Note the sector is `Regional development`, not `Industry, service`.

```text
https://data.1212.mn/api/v1/{lang}/NSO/Regional%20development/Livestock/DT_NSO_1001_109V1.px
```

GET returns metadata; POST a `json-stat2` query selecting every value of each variable. Fetch both `en` and `mn`. Variables: `Малын төрөл` (6), `Бүс` (30), `Он` (56). Year codes are positions (`0` = 2025 ... `55` = 1970), not calendar years; use value labels. Queries and responses are saved in `tools/versions/nso-livestock-by-aimag/v1/raw/`.

## Dimensions

- **Livestock type** (codes 0–5): Total, Horse, Cattle, Camel, Sheep, Goat.
- **Region** (30 codes): `0` national total; groups `1` Khangai, `2` Western, `3` Northern, `4` Central, `5` Eastern, `6` Govi, `7` Ulaanbaatar; 22 leaves (21 aimags + Ulaanbaatar `711`). Region labels carry leading whitespace for hierarchy; trim it. Codes differ from other NSO livestock tables (here Arkhangai is `165` and Ulaanbaatar `711`), so never join on region code across tables; join on the English name.
- **Year**: 1970–2025.

English leaf names (match `livestock-losses-by-aimag` and `hay-prices-by-region`): Arkhangai, Bayan-Ulgii, Bayankhongor, Bulgan, Darkhan-Uul, Dornod, Dornogovi, Dundgovi, Govi-Altai, Govisumber, Khentii, Khovd, Khuvsgul, Orkhon, Selenge, Sukhbaatar, Tuv, Ulaanbaatar, Umnugovi, Uvs, Uvurkhangai, Zavkhan.

## Raw data files

`tools/versions/nso-livestock-by-aimag/v1/data-en.csv` and `data-mn.csv`: long format, 10,080 rows each (6 types x 30 regions x 56 years), sorted by year then source region order then type.

| Column | Values |
|---|---|
| `year` | 1970–2025 |
| `region` | Trimmed source label (EN or MN) |
| `region_level` | `national`, `regional_group`, `aimag` (22 leaves incl. Ulaanbaatar city) |
| `livestock_type` | Total, Horse, Cattle, Camel, Sheep, Goat (MN: Бүгд, Адуу, Үхэр, Тэмээ, Хонь, Ямаа) |
| `value` | Thousand head; blank = missing |

The two languages are row-aligned. "Ulaanbaatar" appears twice: as the group `7` (`regional_group`) and as the city `711` (`aimag`). Filter on `region_level`.

## Missing values and quirks

- 208 blank cells per language (source `..`); 207 are in leaf units, 1 is the Ulaanbaatar group total for 1979. Never convert to 0. Genuine zeros exist (10 cells, camels) and are valid.
- Leaf gaps: Govisumber all types 1970–1990; Orkhon horse/cattle/sheep/goat 1970–1975, total 1970–1975 and 1979, camel 1970–1991; Darkhan-Uul camel 1970–1988 and total 1979; Ulaanbaatar camel 1970–1978 and total 1979.
- Type values do not always sum to Total (Khuvsgul 1980, Selenge 2009). Source values are preserved as published.
- Historical geography follows current region labels; boundaries changed over time (Orkhon, Darkhan-Uul and Govisumber were created later). Do not imply current boundaries applied throughout.
- Aimag values are not guaranteed to sum to the national total or group totals; never add groups to leaves.
- Counts are in thousand head with source precision.

## Splits

| Dataset | Selection | Chart |
|---|---|---|
| `livestock-total-by-aimag` | `livestock_type = Total`, `region_level = aimag` (22 units), all years | Choropleth / ranked bar. EN "Mongolia Livestock by Aimag, Thousand Head (1970–2025)"; MN "Аймаг, нийслэлийн малын тоо, мянган толгой (1970–2025)" |
| `livestock-by-species-by-aimag` | five species (no Total), `region_level = aimag` (22 units), all years, default view 2025 | Stacked horizontal bar per aimag. EN "Mongolia Livestock by Species and Aimag, Thousand Head (1970–2025)"; MN "Аймаг, нийслэлийн малын тоо, төрлөөр, мянган толгой (1970–2025)" |

Downloads keep blanks for missing observations. Related datasets: `livestock-by-type` (national, by species) and `livestock-losses-by-aimag` (adult losses).

## Refresh

Re-run the GET/POST above into a new version directory (`v2`, ...), never overwriting earlier evidence, then regenerate both splits and update the years in titles and excerpts.
