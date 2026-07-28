# Hospital Beds National

**Dataset ID:** `hospital-beds-national`
**Source:** NSO 1212.mn
**Table ID:** DT_NSO_2100_005V3.px

## Description

Total number of hospital beds in Mongolia at the national level from 1989 to 2024. This dataset shows healthcare infrastructure capacity over 35 years.

## Data Structure

**Original table structure:**
- Indicators: Total, Internal medicine, Surgery and traumatology, Ophtalmology, Otolaryngology, Obstetrics, Gyneacology, Neurology, Psychiatry and narcology, Pediatrics, Beds per 1000 population
- Annual: 1989-2024

**Filter applied:**
- Keep only "Total" indicator (aggregate of all bed types)

**Final structure:**
- Year (1989-2024)
- Hospital beds (count)

## Fetch Instructions

```bash
# Fetch raw data from NSO API
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2100_005V3.px --output /path/to/output

# Process and filter
# See tools/scripts/fetch_hospital_beds.py for filtering logic
# Filters for "Total" indicator only
```

## Processing Steps

1. Fetch bilingual data from NSO API (EN and MN)
2. Filter for "Total" indicator only (exclude individual bed types)
3. Create simple 2-column structure: Year, Count
4. Sort by year ascending
5. Export to CSV (EN and MN), XLSX, and chart specs

## Chart Specification

- Type: Area chart (single-series time series)
- X-axis: Year (quantitative)
- Y-axis: Hospital beds (quantitative)
- Color: #3b82f6 (brand blue)
- Features: Gradient fill, hover tooltip

## Update Frequency

Annual (updates typically available in Q2 of following year)

## Notes

- 2021 shows anomaly (35,310 beds) - may be data reporting change
- General trend shows growth from ~18,000 (late 1990s-early 2000s) to ~30,000 (2024)
- Decline in early 1990s corresponds to economic transition period
