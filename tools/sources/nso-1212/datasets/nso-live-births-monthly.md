# Dataset: Mongolia Live Births Monthly

## Identifiers

- **Dataset ID**: `nso-live-births-monthly`
- **Source ID**: `nso-1212`
- **Table ID**: `DT_NSO_2100_018V5.px`

## Description

Monthly live birth counts for Mongolia (national total) from January 2016 to March 2026, sourced from the National Statistics Office of Mongolia (1212.mn).

## Source Data

- **Table**: `DT_NSO_2100_018V5.px`
- **Sector**: Education, health
- **Subsector**: Births, deaths
- **Dimensions**: Region (27 values), Month (YYYY-MM)
- **Filter applied**: Region = "Total" (MN: "Улсын дүн") — national aggregate only

## Output Columns

| Column | Description |
|--------|-------------|
| `month` | Year-month (YYYY-MM format) |
| `births` | Count of live births |

## Coverage

- **Time range**: 2016-01 to 2026-03 (123 months)
- **Geography**: National total
- **Frequency**: Monthly

## Files

- `data.mn/public/datasets/nso-live-births-monthly-en.csv` — English chart data
- `data.mn/public/datasets/nso-live-births-monthly-mn.csv` — Mongolian chart data
- `data.mn/public/datasets/nso-live-births-monthly.xlsx` — Excel download
- `data.mn/public/charts/nso-live-births-monthly-en.json` — EN chart spec
- `data.mn/public/charts/nso-live-births-monthly-mn.json` — MN chart spec

## Update Instructions

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2100_018V5.px --lang both --output /tmp/births_data
```

Then filter rows where Region == "Total" / "Улсын дүн" and re-export CSVs.
