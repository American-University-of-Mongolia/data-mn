# mrpam-mining-permits

Monthly mining permit counts and licensed area by province from MRPAM.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-mining-permits` |
| **Source** | `mrpam` |
| **Source Tables** | 1.1 |
| **Update Frequency** | Monthly |
| **Units** | Count (тоо), Hectares (га) |

## Description

Number of active exploration and extraction licenses, and total licensed area, broken down by province (aimag). Sourced from Table 1.1 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-mining-permits-en.csv`)
```
year,month,province,exploration_count,exploration_area_ha,extraction_count,extraction_area_ha
2025,1,Ulaanbaatar,45,12500.0,120,45000.0
2025,1,Khentii,30,9800.0,85,38000.0
```

### Mongolian (`mrpam-mining-permits-mn.csv`)
```
он,сар,аймаг,хайгуулын_тоо,хайгуулын_талбай_га,ашиглалтын_тоо,ашиглалтын_талбай_га
2025,1,Улаанбаатар,45,12500.0,120,45000.0
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-mining-permits --year 2025
```

## Section Keywords

Search for pages containing: `тусгай зөвшөөрөл`, `1.1`, `хайгуулын`

## Province Names (MN → EN)

| Mongolian | English |
|-----------|---------|
| Улаанбаатар | Ulaanbaatar |
| Архангай | Arkhangai |
| Баян-Өлгий | Bayan-Ulgii |
| Баянхонгор | Bayankhongor |
| Булган | Bulgan |
| Говь-Алтай | Govi-Altai |
| Говьсүмбэр | Govisumber |
| Дархан-Уул | Darkhan-Uul |
| Дорноговь | Dornogovi |
| Дорнод | Dornod |
| Дундговь | Dundgovi |
| Завхан | Zavkhan |
| Орхон | Orkhon |
| Өвөрхангай | Uvurkhangai |
| Өмнөговь | Umnugovi |
| Сүхбаатар | Sukhbaatar |
| Сэлэнгэ | Selenge |
| Төв | Tuv |
| Увс | Uvs |
| Ховд | Khovd |
| Хөвсгөл | Khuvsgul |
| Хэнтий | Khentii |

## Notes

- Table 1.1 is typically on the first 2-3 pages of the report
- Total rows (Нийт дүн) should be excluded from per-province data
