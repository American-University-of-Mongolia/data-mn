# Dataset: Mongolia Live Births by Region (Monthly)

## Identifiers

- **Dataset ID**: `nso-live-births-by-region-monthly`
- **Source ID**: `nso-1212`
- **Table ID**: `DT_NSO_2100_018V5.px`

## Description

Monthly live births by aimag, Ulaanbaatar and the four economic regions, January 2016 to September 2026.

## Output

- Chart CSV (`-en`/`-mn`): 4 regions + Ulaanbaatar; columns `region, month, births`
- Download CSV (`-all-*`): 21 aimags + Ulaanbaatar (the "Total" row and region aggregates are excluded)
- XLSX: wide format, sheets "English" and "Монгол"

## Update Instructions

```bash
cd .claude/skills/datamn-source-nso
PYTHONUTF8=1 python fetch_data.py --table DT_NSO_2100_018V5.px --lang both --output /tmp/births
```

Drop Region == Total, split aggregates (Western/Khangai/Central/Eastern region) from aimags, and export.
