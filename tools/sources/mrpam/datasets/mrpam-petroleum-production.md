# mrpam-petroleum-production

Monthly petroleum production and export from MRPAM.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-petroleum-production` |
| **Source** | `mrpam` |
| **Source Tables** | 4.1, 4.2 |
| **Update Frequency** | Monthly |
| **Units** | Barrels (баррель) |

## Description

Monthly petroleum (crude oil) production and export volumes in barrels. Sourced from Tables 4.1 and 4.2 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-petroleum-production-en.csv`)
```
year,month,production_barrels,export_barrels
2025,1,1250000,980000
```

### Mongolian (`mrpam-petroleum-production-mn.csv`)
```
он,сар,олборлолт_баррель,экспорт_баррель
2025,1,1250000,980000
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-petroleum-production --year 2025
```

## Section Keywords

Search for pages containing: `газрын тос`, `4.1`, `4.2`, `баррель`

## Notes

- Production figures are typically daily averages or monthly totals — verify units from table header
- Export volumes may be expressed in both barrels and cubic meters in different years
