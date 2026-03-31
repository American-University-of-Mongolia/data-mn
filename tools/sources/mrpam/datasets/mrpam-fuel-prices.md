# mrpam-fuel-prices

Retail fuel prices by province and monthly trend from MRPAM.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-fuel-prices` |
| **Source** | `mrpam` |
| **Source Tables** | 4.6, 4.7 |
| **Update Frequency** | Monthly |
| **Units** | MNT per liter (төгрөг/литр) |

## Description

Retail fuel prices (gasoline AI-92, AI-95, diesel, LPG) by province (Table 4.6) and monthly time series (Table 4.7). Sourced from the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-fuel-prices-en.csv`)
```
year,month,province,gasoline_price,diesel_price
2025,1,Ulaanbaatar,2850,2900
2025,1,Arkhangai,3050,3100
```

### Mongolian (`mrpam-fuel-prices-mn.csv`)
```
он,сар,аймаг,бензин_үнэ,дизель_үнэ
2025,1,Улаанбаатар,2850,2900
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-fuel-prices --year 2025
```

## Section Keywords

Search for pages containing: `шатахуун`, `4.6`, `бензин`, `дизель`

## Notes

- Table 4.6 = prices by province (cross-sectional)
- Table 4.7 = monthly trend (time series) — may be a separate dataset split later
- AI-92 and AI-95 gasoline grades are both reported; use the more widely available grade
