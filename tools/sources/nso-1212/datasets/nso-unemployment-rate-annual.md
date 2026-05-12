# Dataset: nso-unemployment-rate-annual

## Description

Mongolia's national unemployment rate by sex (Total, Male, Female) from 2009 to 2024, annual frequency.

## Source

- **Source ID**: nso-1212
- **Table ID**: DT_NSO_0400_020V2_10.px
- **Table Name**: UNEMPLOYMENT RATE, by age group, gender, region, aimags and the Capital, by annual
- **Sector**: Regional development / Labour and business
- **URL**: https://1212.mn

## Fetch Instructions

```bash
cd .claude/skills/datamn-source-nso
conda run -n datamn python3 fetch_data.py --table DT_NSO_0400_020V2_10.px --output /tmp/unemployment_raw --lang en
conda run -n datamn python3 fetch_data.py --table DT_NSO_0400_020V2_10.px --output /tmp/unemployment_raw --lang mn
```

## Filters Applied

- Region = "Total" (national aggregate)
- Age group = "Total" (all age groups)
- Gender = all (Total, Male, Female)

## Output Columns

- EN: `year`, `sex`, `unemployment_rate`
- MN: `жил`, `хүйс`, `ажилгүйдлийн_түвшин`

## Sex Labels

- EN: Total, Male, Female
- MN: Нийт, Эрэгтэй, Эмэгтэй

## Coverage

- Geography: National (Улсын дүн)
- Granularity: national
- Time range: 2009–2024
- Frequency: annual
