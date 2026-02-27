# Dataset: Electricity Balance

## Identification

- **ID**: `electricity-balance`
- **Source**: `nso-1212`
- **Category**: Infrastructure
- **Tags**: [electricity, energy, infrastructure, power, generation, imports]

## Source Reference

- **Table ID**: `DT_NSO_1100_009V1.px`
- **Sector**: `Industry, service`
- **Subsector**: `Industry`

## Title

- **EN**: Mongolia Electricity Balance: Generation, Imports, and Consumption (1989-2024)
- **MN**: Монгол Улсын цахилгаан эрчим хүчний баланс: үйлдвэрлэл, импорт, хэрэглээ (1989-2024)

## Description

Annual electricity balance for Mongolia showing gross generation, imports, and total consumption in million kWh (GWh). Data spans from 1989 to 2024, covering the transition from Soviet-era infrastructure to modern energy systems.

## Variables

### Indicators (Үзүүлэлтүүд)
Source table has 14 indicators. The main dataset uses 3 key indicators:
- `Gross generation` / `Үйлдвэрлэсэн` — Domestic electricity production
- `Imports` / `Импорт` — Electricity imported (primarily from Russia)
- `Consumption` / `Хэрэглэсэн` — Total electricity consumed

The "all" CSV files include all 14 indicators (consumption by sector, losses, exports, per capita).

### Year (Он)
36 years: 1989-2024

## Update Instructions

Query the API for table `DT_NSO_1100_009V1.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1100_009V1.px --output ./output
```

## Notes

- Values are in million kWh (equivalent to GWh)
- Mongolia imports electricity primarily from Russia
- Imports grew dramatically from ~160 million kWh (1989) to 2,753 million kWh (2024)
- Consumption exceeds domestic generation since ~2012, with the gap filled by imports
