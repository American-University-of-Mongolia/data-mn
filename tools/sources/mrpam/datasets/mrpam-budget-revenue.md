# mrpam-budget-revenue

State budget revenue from the mining sector from MRPAM monthly reports.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-budget-revenue` |
| **Source** | `mrpam` |
| **Source Tables** | 5.1 |
| **Update Frequency** | Monthly |
| **Units** | Billion MNT (тэрбум төгрөг) |

## Description

Plan vs. actual state budget revenue from the mining and petroleum sector, broken down by revenue type. Sourced from Table 5.1 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-budget-revenue-en.csv`)
```
year,month,revenue_type,plan_bln_mnt,actual_bln_mnt,pct_of_plan
2025,1,Mineral royalty,450.0,420.5,93.4
2025,1,Corporate income tax,380.0,395.2,104.0
```

### Mongolian (`mrpam-budget-revenue-mn.csv`)
```
он,сар,орлогын_төрөл,төлөвлөгөө_тэрбум,гүйцэтгэл_тэрбум,хувь
2025,1,Ашигт малтмалын нөөц ашигласны төлбөр,450.0,420.5,93.4
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-budget-revenue --year 2025
```

## Section Keywords

Search for pages containing: `улсын төсвийн орлого`, `5.1`, `төсөв`

## Common Revenue Type Names (MN → EN)

| Mongolian | English |
|-----------|---------|
| Ашигт малтмалын нөөц ашигласны төлбөр | Mineral royalty |
| Газрын тосны нөөц ашигласны төлбөр | Petroleum royalty |
| Аж ахуйн нэгжийн орлогын татвар | Corporate income tax |
| Нийт | Total |
