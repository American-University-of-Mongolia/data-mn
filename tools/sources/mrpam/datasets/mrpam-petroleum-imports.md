# mrpam-petroleum-imports

Petroleum product imports by type from MRPAM monthly reports.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-petroleum-imports` |
| **Source** | `mrpam` |
| **Source Tables** | 4.3 |
| **Update Frequency** | Monthly |

## Description

Monthly imports of petroleum products (gasoline, diesel, LPG, kerosene, etc.) by product type. Sourced from Table 4.3 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-petroleum-imports-en.csv`)
```
year,month,product,volume,unit
2025,1,Gasoline AI-92,85000,tonnes
2025,1,Diesel,210000,tonnes
2025,1,LPG,12000,tonnes
```

### Mongolian (`mrpam-petroleum-imports-mn.csv`)
```
он,сар,бүтээгдэхүүн,хэмжээ,нэгж
2025,1,АИ-92 бензин,85000,тонн
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-petroleum-imports --year 2025
```

## Section Keywords

Search for pages containing: `импорт`, `4.3`, `шатахуун импорт`

## Common Product Names (MN → EN)

| Mongolian | English |
|-----------|---------|
| АИ-92 бензин | Gasoline AI-92 |
| АИ-95 бензин | Gasoline AI-95 |
| Дизель түлш | Diesel fuel |
| Шингэрүүлсэн газ (LPG) | LPG |
| Керосин | Kerosene |
| Мазут | Fuel oil (mazut) |
