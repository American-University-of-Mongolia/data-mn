# Dataset: Mongolia Marriages and Divorces (2006–2025)

## Type: STANDALONE DATASET

## Identifiers

- **Dataset ID**: `nso-marriages-divorces-annual`
- **Source ID**: `nso-1212`
- **Table ID**: `DT_NSO_0300_018V2.px`
- **Sector**: Population, household
- **Subsector**: 2_Regular movement of population

## Description

Annual counts of marriages and divorces in Mongolia from 2006 to 2025 (2012 missing from source), at the national level. Sourced from the National Statistics Office via 1212.mn API.

## Variables

| Column | Type | Description |
|--------|------|-------------|
| Indicator | nominal | "Marriage" or "Divorces" |
| Region | nominal | Geographic area; filter to "Total" for national |
| Year | integer | 2006–2025 (2012 absent) |
| value | integer | Count |

## Data Processing

1. Fetch via `fetch_data.py --table DT_NSO_0300_018V2.px`
2. Filter `Region == "Total"` (EN) / `Бүс == "Улсын дүн"` (MN)
3. Rename columns: Indicator→indicator, Year→year, value→count
4. Sort by year, indicator

## Chart Type

Multi-line: one line per indicator (Marriage / Divorces).
- Marriage: `#4c78a8`
- Divorces: `#e45756`
