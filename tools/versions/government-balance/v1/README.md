# Government Balance - Version 1

## Dataset Information

- **Dataset ID**: government-balance
- **Version**: 1
- **Parent**: nso-government-budget
- **Source**: NSO 1212.mn (DT_NSO_0800_001V1.px)
- **Created**: 2026-01-29

## Description

Split dataset showing government budget balance (revenue - expenditure) from 1991-2025.

## Source Data

Raw data is stored in parent dataset: `tools/versions/nso-government-budget/v1/`

## Split Filter

```json
{
  "indicator": ["Balance"]
}
```

## Output Files

- `data.mn/public/datasets/government-balance-en.csv`
- `data.mn/public/datasets/government-balance-mn.csv`
- `data.mn/public/datasets/government-balance.xlsx`

## Notes

This is a split dataset that filters the Balance indicator from the parent government budget table.
