# Dataset: Infant Mortality Rate (National)

## Identification
- **ID**: infant-mortality-rate-national
- **Category**: Health
- **Tags**: [health, infant-mortality, mortality, demographics]

## Source Reference
- **Table ID**: DT_NSO_2100_015V1.px
- **URL**: https://1212.mn
- **Title**: INFANT MORTALITY RATE, per 1000 live births, aimags and the Capital and by month

## Variables

### Бүс (Region)
- `Улсын дүн`: National total (used for this dataset)
- Other values: 21 aimags + Ulaanbaatar + regional summaries

### Сар (Month)
- Monthly data from 2016-01 to 2025-12
- Format: YYYY.MM

## Update Instructions

### Check for Updates
```bash
cd .claude/skills/datamn-source-nso
python3 query_api.py --detailed "infant mortality rate monthly"
```

### Fetch Data
```bash
python3 fetch_data.py
# Filter for table DT_NSO_2100_015V1.px
# Filter region = "Улсын дүн" (National total)
```

### Validation
- Rate values should be between 0 and 50 per 1,000 live births
- Monthly data should have no gaps
- Both EN and MN CSVs must have identical numeric values
