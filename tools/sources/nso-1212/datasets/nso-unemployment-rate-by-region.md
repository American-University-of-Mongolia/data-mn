# nso-unemployment-rate-by-region

## Source

Table: `DT_NSO_0400_020V2_10.px`  
Path: Regional development / Labour and business / UNEMPLOYMENT RATE, by age group, gender, region, aimags and the Capital, by annual

## Description

Annual unemployment rate (%) for all 22 aimags and Ulaanbaatar, 2009–2024. Filtered to Age group = Total, Gender = Total.

## Fetch Commands

```bash
cd .claude/skills/datamn-source-nso
conda run -n datamn python3 fetch_data.py --table DT_NSO_0400_020V2_10.px --output /tmp/unemp_region_raw --lang en
conda run -n datamn python3 fetch_data.py --table DT_NSO_0400_020V2_10.px --output /tmp/unemp_region_raw --lang mn
```

## Filters Applied

- Age group: Total (EN) / Бүгд (MN)
- Gender: Total (EN) / Нийт (MN)
- Excluded regional aggregates (Central, Eastern, Western, Khangai, North, Govi regions and national total)

## Chart Featured Aimags

Govisumber, Darkhan-Uul, Bayan-Ulgii, Khuvsgul, Orkhon, Ulaanbaatar (highest 2024 unemployment)

## Output Columns

EN: year, region, unemployment_rate  
MN: жил, аймаг, ажилгүйдлийн_түвшин
