# Dataset: GDP by Economic Sector

- **ID**: `gdp-by-sector`
- **Parent**: `nso-gdp-by-economic-activity`
- **Table ID**: `DT_NSO_0500_001V1.px`
- **Category**: Economy
- **Frequency**: Annual

## Transformation

Filter the parent table to `GDP, at current prices`, the latest year, and all
economic activities except `Total`. Export bilingual `sector,value` CSVs and
the complete English Excel workbook.

## Update

Regenerate whenever `nso-gdp-by-economic-activity` changes. The current
published period is 2025.
