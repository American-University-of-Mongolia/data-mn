# Dataset: MNT Lending Rate (Monthly)

## Identification

- **ID**: `mongolbank-lending-rate-mnt-monthly`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, lending rate, interest rate, MNT, banking, monthly]

## Source Reference

- **Portal**: https://www.mongolbank.mn/mn/p/interest-rate-statistics
- **Script**: Data extracted from `mongolbank-reference-rates-all-en.csv` (the portal is JS-rendered and not directly scrapable). The reference-rates CSV contains rate_type `"Lending Rate (MNT, newly issued)"` derived from stat API indicator 171821 (`Weighted interest rate of total issued loans (MNT)`).
- **Language**: MN-only source (translated)

## Title

- **EN**: Mongolia MNT Lending Rate, Monthly (2016–2026)
- **MN**: Монгол Улсын төгрөгийн зээлийн хүү, сар бүр (2016–2026)

## Description

Monthly weighted average interest rate on MNT-denominated loans issued by Mongolia's banking system.
Sourced from the Bank of Mongolia interest rate statistics portal (stat API indicator 171821).
Data begins March 2016 (119 rows through January 2026). Dates are stored as YYYY-MM (first of month).

## Distinction from mongolbank-reference-rates

`mongolbank-reference-rates` uses the stat.mongolbank.mn API directly and includes lending and deposit rates (MNT + FX) in multi-series format. This dataset:
- Is single-purpose (MNT lending rate only)
- Excludes deposit rates and FX series

## Variables

- **date** (огноо): Year-month of observation, format YYYY-MM
- **lending_rate_pct** (зээлийн_хүү_хувь): Monthly weighted average MNT lending rate (%)

## Update Instructions

To update: re-run `mongolbank-reference-rates-all-en.csv` fetch (stat API indicator 171821), then filter to `"Lending Rate (MNT, newly issued)"` and re-export both CSV files and XLSX.

Note: Registry `version` and file path fields are not automatically populated by the CLI — consistent with all other mongolbank datasets.
