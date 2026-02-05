# Inbound Passengers - Tourism

## Dataset Information

**ID**: `inbound-passengers-tourism`
**Parent**: `nso-inbound-passengers-by-region-purpose`
**Type**: Split Dataset
**Source**: NSO 1212.mn
**Table ID**: `DT_NSO_1800_005V2.px`

## Description

Foreign passengers arriving in Mongolia for tourism purposes from 2006 to 2025. This split dataset extracts only tourism-related arrivals from the complete inbound passengers table.

## Split Filter

```json
{
  "purpose": ["Tourism"]
}
```

## Data Structure

### Source Table Dimensions
- **Purpose**: Business, Tourism, Work, Study, Personal, Transit, etc.
- **Region**: Geographic regions of origin
- **Year**: 2006-2025

### Split Output
- **year**: 2006-2025
- **passengers**: Number of tourist arrivals

## Data Characteristics

- **Temporal Coverage**: 2006-2025
- **Geographic Coverage**: National (all entry points)
- **Frequency**: Annual
- **Unit**: Number of passengers

## Files Generated

### Chart Data
- `inbound-passengers-tourism-en.csv`
- `inbound-passengers-tourism-mn.csv`

### Visualizations
- `inbound-passengers-tourism-en.json`
- `inbound-passengers-tourism-mn.json`

### MDX Pages
- `en/inbound-passengers-tourism.mdx`
- `mn/inbound-passengers-tourism.mdx`

## Key Statistics

- **Year Range**: 2006-2025
- **Peak Tourism Year**: 2025 (417,935 tourists)
- **COVID Impact**: 2020-2021 saw dramatic decline (7,798 and 1,010 respectively)
- **Recovery**: Strong post-pandemic recovery from 2022 onwards

## Notes

- Tourism is the largest purpose category for foreign arrivals
- Data shows significant growth trend interrupted by COVID-19
- Post-pandemic recovery exceeds pre-pandemic levels

## Update Frequency

Annual updates from NSO

## Last Updated

2026-01-29
