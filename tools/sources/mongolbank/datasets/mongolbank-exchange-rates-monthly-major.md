# Dataset: Monthly Average Exchange Rates (Major Currencies)

## Identification

- **ID**: `mongolbank-exchange-rates-monthly-major`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, exchange rates, currency, MNT, finance, monthly]

## Source Reference

- **Portal**: https://www.mongolbank.mn/mn/currency-rate-movement/monthly
- **Script**: `.claude/skills/datamn-source-mongolbank/fetch_exchange_rates.py`
- **Currencies**: USD, EUR, CNY, RUB, JPY, KRW

## Title

- **EN**: Mongolia Monthly Average Exchange Rates, Major Currencies (2020–2026)
- **MN**: Монгол Улсын сарын дундаж валютын ханш, гол валютууд (2020–2026)

## Description

Monthly average exchange rates for USD, EUR, CNY, RUB, JPY, and KRW against the Mongolian Tugrik (MNT).
Derived by computing the arithmetic mean of all official daily closing rates within each calendar month.

## Aggregation Method

Daily → Monthly: arithmetic mean of closing rates per currency per calendar month.
Each date is set to the first day of the month (YYYY-MM-01) as the period identifier.

## Variables

- **date** (огноо): First day of month, ISO format YYYY-MM-DD
- **currency_code** (валютын_код): ISO 4217 code (USD, EUR, CNY, RUB, JPY, KRW)
- **currency_name** (валютын_нэр): Full currency name in respective language
- **rate_mnt** (ханш_төгрөг): Monthly average MNT per 1 unit of foreign currency, rounded to 4dp

## Distinction from mongolbank-exchange-rates-daily

This dataset provides monthly averages for trend analysis. The daily dataset
(`mongolbank-exchange-rates-daily`) provides exact closing rates for each business day.

## Update Instructions

1. Run `fetch_exchange_rates.py --start <last_date> --output /tmp/new-daily`
2. Re-run aggregation script to recompute monthly averages (or append new months)
3. Copy updated CSVs to `data.mn/public/datasets/` and `tools/versions/v1/`

## Validation

- All rate values > 0
- 6 currencies per month (USD, EUR, CNY, RUB, JPY, KRW)
- No gaps in monthly sequence
- EN and MN CSVs have identical numeric values
