# Dataset: nso-deaths-monthly

**Table ID**: DT_NSO_2100_027V2.px
**Source**: NSO 1212.mn (nso-1212)
**Category**: Demographics / Хүн ам зүй

## Description

Monthly death counts for Mongolia from January 2016 onward, by region and national total.

## Fetch Instructions

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2100_027V2.px --output /tmp/deaths_data
```

## Transformation

- Filter `Region == "Total"` (EN) / `Бүс == "Улсын дүн"` (MN) for national aggregate
- Keep columns: Month/Сар, value
- Rename: month, deaths / сар, нас_баралт
- Normalize month to YYYY-MM format (zero-pad single-digit months)
- Sort ascending by month

## Columns

| Column | Type | Description |
|--------|------|-------------|
| month | string | Year-Month (YYYY-MM) |
| deaths | integer | Number of deaths |
