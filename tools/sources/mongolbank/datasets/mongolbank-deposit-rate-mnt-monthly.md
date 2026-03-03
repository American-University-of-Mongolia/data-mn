# Dataset: MNT Deposit Rate (Monthly)

## Identification

- **ID**: `mongolbank-deposit-rate-mnt-monthly`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, deposit rate, interest rate, MNT, banking, monthly]

## Source Reference

- **Portal**: https://www.mongolbank.mn/mn/p/interest-rate-statistics
- **Script**: `.claude/skills/datamn-source-mongolbank/fetch_bulletin_table.py --indicator deposit-rate`
- **Language**: MN-only source (translated via fetch_bulletin_table.py)

## Title

- **EN**: Mongolia MNT Deposit Rate, Monthly (2008–2026)
- **MN**: Монгол Улсын төгрөгийн хадгаламжийн хүү, сар бүр (2008–2026)

## Description

Monthly weighted average interest rate on MNT-denominated bank deposits in Mongolia.
Sourced from the Bank of Mongolia interest rate statistics portal via the `stat.mongolbank.mn`
statistics API (indicator 84982: Deposit weighted average rate, MNT, outstanding).

## Distinction from mongolbank-reference-rates

`mongolbank-reference-rates` uses the `stat.mongolbank.mn` direct API and includes
both lending and deposit rates (MNT + FX) in a multi-series format. This dataset:
- Uses the same underlying API data (indicator 84982)
- Is single-purpose (MNT deposit rate only)
- Excludes FX deposit rates
- Presents data in a tidy single-series format suitable for time-series analysis

## FX Availability Decision

The source data (stat.mongolbank.mn API, report 142) includes both a MNT deposit rate
(indicator 84982) and an FX deposit rate (indicator 84992). This dataset retains only the
MNT deposit rate (indicator 84982). The FX deposit rate is available separately in
`mongolbank-reference-rates`. Zero-value rows (2009-2010 quarterly-only reporting periods)
were excluded as they represent data gaps, not actual zero rates.

## Variables

- **date** (огноо): First day of month, ISO format YYYY-MM-DD
- **deposit_rate_pct** (хадгаламжийн_хүү_хувь): Monthly weighted average MNT deposit rate (%)

## Update Instructions

```bash
cd .claude/skills/datamn-source-mongolbank
conda run -n datamn python3 fetch_bulletin_table.py --indicator deposit-rate --output /tmp/deposit-rate
```

If the portal scraper fails, fetch directly from the stat API (indicator 84982, report 142, parentId 140).
Then apply MNT filter if needed and copy files to:
- `data.mn/public/datasets/mongolbank-deposit-rate-mnt-monthly-en.csv`
- `data.mn/public/datasets/mongolbank-deposit-rate-mnt-monthly-mn.csv`
- `tools/versions/mongolbank-deposit-rate-mnt-monthly/v1/`
