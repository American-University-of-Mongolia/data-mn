# Average Wages by Sector

## Source Table
- **Table ID**: `DT_NSO_0400_022V1.px` (annual sub-table: by SEX, SECTOR, TIME ANNUAL; sibling V2 = quarterly, V3 = monthly)
- **Sector**: Labour, business
- **Subsector**: Wages
- **Parent**: MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities (name-keyed group id)
- **Parent dataset**: `salary-average-national` (registry `parent_id`; same NSO table, see its definition)
- **Note (2026-09-08 table switch)**: the NSO catalog moved wage tables to name-string group ids; the flat `DT_NSO_0400_022V1.px` reference no longer resolves directly (HTTP 400). The table is fetched via the name-keyed group path `MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities/DT_NSO_0400_022V1.px`. Coverage is unchanged (2001-2025, 22 sectors incl. National average, SEX split TOTAL/FEMALE/MALE).

## API Path
```
GET /api/v1/{lang}/NSO/Labour%2C%20business/Wages/MONTHLY%20AVERAGE%20NOMINAL%20WAGES%2C%20by%20division%20of%20economic%20activities/DT_NSO_0400_022V1.px
```

Note: This table is nested under a parent grouping. The URL must include the parent table name; since the 2026-09-08 table switch that group is a name-keyed id, so always use the full group path above (never the bare `DT_NSO_0400_022V1.px`).

## Dimensions
1. **Sex** (Хүйс): TOTAL, FEMALE, MALE
2. **Sector** (Салбар): 22 economic sectors including National average
3. **Year** (ОН): 2001-2025 (25 years)

## Split: average-wages
- **Filter**: Sex = TOTAL only, top 8 sectors
- **Sectors**: Mining, Finance & Insurance, IT & Communication, Construction, Education, Manufacturing, Agriculture, National Average
- **Format**: Long format (Sector, Year, Salary)
- **Chart**: Multi-line chart showing wage trends over time
- **Rows**: 8 sectors x 25 years = 200

### Sector labels (chart files)
The 8-sector chart files use short labels (and this row order within each year); the NSO names are used in the `-all-` files.

| EN label | NSO sector (EN) | MN label | NSO sector (MN) |
|----------|-----------------|----------|-----------------|
| Mining | Mining and quarrying | Уул уурхай | Уул уурхай, олборлолт |
| Finance & Insurance | Financial and insurance activities | Санхүү, даатгал | Санхүүгийн болон даатгалын үйл ажиллагаа |
| IT & Communication | Information and communication | Мэдээлэл, холбоо | Мэдээлэл, холбоо |
| Construction | Construction | Барилга | Барилга |
| Education | Education | Боловсрол | Боловсрол |
| Manufacturing | Manufacturing | Боловсруулах үйлдвэрлэл | Боловсруулах үйлдвэрлэл |
| Agriculture | Agriculture, forestry, fishing and hunting | Хөдөө аж ахуй | Хөдөө аж ахуй, ойн аж ахуй, загас барилт, ан агнуур |
| National Average | National average | Улсын дундаж | Улсын дундаж |

## All data
- **Filter**: Sex = TOTAL only, all 22 sectors
- **Format**: Long format (Sector, Year, Salary)
- **Rows**: 22 sectors x 25 years = 550

## Refresh
- No separate fetch: regenerate from the parent's current raw files (`tools/versions/salary-average-national/v{N}/nso-annual-raw-{en,mn}.csv`, SEX = TOTAL; `Бүгд` in the MN file; MN sector names carry NSO indentation that must be stripped).
- Row order: year ascending, then sector (label order above for the chart files, NSO table order for the `-all-` files). Values are kept as the raw strings (one decimal, e.g. `808.0`); missing values stay blank.
- Downloads: the XLSX is the bilingual wide workbook ("English" and "Монгол" sheets) built from the `-all-` CSVs with the `tools/scripts/rebuild_downloads.py` helpers.
- v2 (2026-10): extended 2001-2024 to 2001-2025 from `salary-average-national` v3 raw (NSO table updated 2026-05-04T16:27:24); no 2001-2024 value was revised.

## Related Datasets (Same Source Table)
- `salary-average-national`: National average salary over time (single line area chart)
- `salary-by-sector-2024`: All 21 sectors for 2024 only (horizontal bar chart)
- `average-wages`: Top 8 sectors over time (multi-line chart) — **this dataset**

## Coverage Note
All three datasets use the same NSO table (DT_NSO_0400_022V1.px) but show different views:
1. `salary-average-national` — time dimension only (national aggregate)
2. `salary-by-sector-2024` — sector dimension only (latest year snapshot)
3. `average-wages` — both sector AND time dimensions (sector trends)

## Values
- Unit: MNT thousands (1000s)
- Monthly average nominal wages
- Some sectors have missing data for earlier years (e.g., IT & Communication has no values before 2013; the cells stay blank)
