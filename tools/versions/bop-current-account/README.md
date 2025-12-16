# Dataset Version History: bop-current-account

## Dataset Information

- **ID**: `bop-current-account`
- **Type**: Split dataset (derived from parent)
- **Parent**: `nso-bop-monthly`
- **Source**: NSO 1212.mn
- **Table**: `DT_NSO_0100_001V10.px`

## Split Filter

```json
{
  "indicator": "I. CURRENT ACCOUNT"
}
```

## Version Structure

Each version directory (`v1/`, `v2/`, etc.) contains:

- `data-en.csv` - English version of filtered data (chart data)
- `data-mn.csv` - Mongolian version of filtered data (chart data)
- `data.xlsx` - Excel export (wide format)

## Update Process

This dataset does NOT fetch data directly from the API. Instead:

1. Wait for parent dataset `nso-bop-monthly` to update
2. Load parent data from `../nso-bop-monthly/nso-0100-001v10-{lang}.csv`
3. Apply filter: `indicator == "I. CURRENT ACCOUNT"`
4. Save filtered data to new version directory

## Notes

- Data is automatically derived when parent updates
- No need to manually fetch from API
- See dataset definition at: `tools/sources/nso-1212/datasets/bop-current-account.md`
