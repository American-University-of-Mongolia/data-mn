# Inbound Foreign Passengers by Region and Purpose - Parent Dataset

## Overview

**Dataset ID**: `nso-inbound-passengers-by-region-purpose`
**Type**: Parent Dataset (raw multi-dimensional data)
**Source**: NSO 1212.mn (DT_NSO_1800_005V2.px)
**Category**: Tourism
**Version**: 1
**Fetched**: 2026-01-29

## Data Structure

- **Rows**: 1,440
- **Columns**: 4
  - `geographical_region` (EN) / `бүс_нутаг` (MN)
  - `purpose_of_visit` (EN) / `аяллын_зорилго` (MN)
  - `year` (EN) / `он` (MN)
  - `value`

## Dimensions

### Geographical Regions (8 values)
- Total
- America
- Africa
- Europe
- East Asia and the Pacific
- Middle East
- South Asia
- Stateless

### Purpose of Visit (9 values)
- Total
- Business
- Personal
- Tourism
- Work
- Transit
- Study
- Permanent residence
- Other

### Time Range
- **Years**: 2006-2025 (20 years)

## Total Combinations
8 regions × 9 purposes × 20 years = 1,440 rows

## Split Datasets

This parent dataset will be split into 4 user-friendly datasets:

1. **inbound-passengers-total** - Total passengers over time (all regions, all purposes)
2. **inbound-passengers-by-region** - Passengers by geographical region (total purposes)
3. **inbound-passengers-by-purpose** - Passengers by purpose of visit (all regions)
4. **inbound-passengers-tourism-only** - Tourism-specific passengers by region

## Files

- `nso-1800-005v2-en.csv` - Raw API response (English)
- `nso-1800-005v2-mn.csv` - Raw API response (Mongolian)
- `data-en.csv` - Cleaned parent dataset (English)
- `data-mn.csv` - Cleaned parent dataset (Mongolian)

## Notes

- Parent datasets do NOT have MDX pages or charts
- Only split datasets are published to the website
- All string values have been cleaned (whitespace trimmed)
- Column names normalized to lowercase with underscores
