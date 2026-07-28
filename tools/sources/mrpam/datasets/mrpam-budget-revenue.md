# mrpam-budget-revenue

State budget revenue from the mining sector from MRPAM monthly reports.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-budget-revenue` |
| **Source** | `mrpam` |
| **Source Tables** | 5.1 / 6.1 |
| **Update Frequency** | Monthly |
| **Units** | Million MNT (сая төгрөг) |

## Description

Plan vs. actual state budget revenue from the mining and petroleum sector, broken down by revenue type. Sourced from Table 5.1 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-budget-revenue-all-en.csv`)
```
year,month,revenue_type,plan_mln_mnt,actual_mln_mnt,pct_of_plan
2026,6,Total,293986.9,191971.7,65.3
```

### Mongolian (`mrpam-budget-revenue-all-mn.csv`)
```
он,сар,орлогын_төрөл,төлөвлөгөө_сая_төг,гүйцэтгэл_сая_төг,хувь
2026,6,БҮГД,293986.9,191971.7,65.3
```

The chart CSVs contain only the `Total` / `БҮГД` series for a readable
plan-versus-actual comparison. The `-all-` CSVs and XLSX workbook contain every
revenue category reported by MRPAM.

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-budget-revenue --year 2025
```

## Section Keywords

Search for pages containing: `улсын төсвийн орлого`, `5.1`, `төсөв`

Reports from 2021 and early 2022 number the source table `6.1`; later reports
number the same table `5.1`. Match the full budget-revenue heading and accept
either number so that unrelated table 5.1 content is not extracted.

## Common Revenue Type Names (MN → EN)

| Mongolian | English |
|-----------|---------|
| Ашигт малтмалын нөөц ашигласны төлбөр | Mineral royalty |
| Газрын тосны нөөц ашигласны төлбөр | Petroleum royalty |
| Аж ахуйн нэгжийн орлогын татвар | Corporate income tax |
| Ашигт малтмалын тусгай зөвшөөрлийн төлбөр | Mineral licence fees |
| Улсын төсвийн хөрөнгөөр хайгуул хийсэн ордын нөхөн төлбөр | Reimbursement for state-funded exploration |
| Газрын тосны экспорт | Petroleum exports |
| Газрын тосны үйлчилгээний орлого | Petroleum service revenue |
| Ашигт малтмалын үйлчилгээний орлого | Mineral services revenue |
| Бусад орлого | Other revenue |
| Сонгон шалгаруулалт | Tender revenue |
| Нийт | Total |
| БҮГД | Total |
