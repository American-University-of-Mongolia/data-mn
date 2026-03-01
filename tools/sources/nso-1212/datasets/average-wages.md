# Average Wages by Sector

## Source Table
- **Table ID**: `DT_NSO_0400_022V1.px`
- **Sector**: Labour, business
- **Subsector**: Wages
- **Parent**: MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities

## API Path
```
GET /api/v1/{lang}/NSO/Labour%2C%20business/Wages/MONTHLY%20AVERAGE%20NOMINAL%20WAGES%2C%20by%20division%20of%20economic%20activities/DT_NSO_0400_022V1.px
```

Note: This table is nested under a parent grouping. The URL must include the parent table name.

## Dimensions
1. **Sex** (Хүйс): TOTAL, FEMALE, MALE
2. **Sector** (Салбар): 22 economic sectors including National average
3. **Year** (ОН): 2001-2024 (24 years)

## Split: average-wages
- **Filter**: Sex = TOTAL only, top 8 sectors
- **Sectors**: Mining, Finance & Insurance, IT & Communication, Construction, Education, Manufacturing, Agriculture, National Average
- **Format**: Long format (Sector, Year, Salary)
- **Chart**: Multi-line chart showing wage trends over time
- **Rows**: 8 sectors x 24 years = 192

## All data
- **Filter**: Sex = TOTAL only, all 22 sectors
- **Format**: Long format (Sector, Year, Salary)
- **Rows**: 22 sectors x 24 years = 528

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
- Some sectors have missing data for earlier years (e.g., IT & Communication before 2005)
