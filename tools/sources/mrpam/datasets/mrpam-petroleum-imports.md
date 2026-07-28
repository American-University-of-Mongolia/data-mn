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

Monthly imports of petroleum products by product type, measured in tonnes.
Sourced from Table 4.3 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-petroleum-imports-en.csv`)
```
year,month,product,volume_t
2026,6,Gasoline AI-92,57353
2026,6,Gasoline AI-92 Euro-5,521
2026,6,Gasoline AI-95,
```

### Mongolian (`mrpam-petroleum-imports-mn.csv`)
```
он,сар,бүтээгдэхүүн,хэмжээ_тн
2026,6,Автобензин АИ-92,57353
2026,6,АИ-92 /Евро-5/,521
2026,6,Автобензин АИ-95,
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

## Schema Changes

- Through January 2024, Table 4.3 has nine positions: Total, A-80, AI-92,
  AI-95, AI-98, diesel, jet fuel TS-1, LPG, and Other.
- From February 2024 through January 2026, AI-98 is omitted.
- From February 2026, the nine positions are Total, AI-92, AI-92 Euro-5,
  AI-95, diesel, diesel Euro-5, jet fuel TS-1, LPG, and Other.
- Empty cells and `-` remain null. Product labels must be assigned by their
  source column position before null rows are filtered or aggregated.
