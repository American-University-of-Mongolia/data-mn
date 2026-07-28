# mrpam-mining-permits

Monthly mining permit counts and licensed area by province from MRPAM.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-mining-permits` |
| **Source** | `mrpam` |
| **Source Tables** | 1.1 |
| **Update Frequency** | Monthly |
| **Units** | Count (тоо), Thousand hectares (мян.га) |

## Description

Number of active exploration and extraction licenses, and total licensed area, broken down by province (aimag). Sourced from Table 1.1 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-mining-permits-all-en.csv`)
```
year,month,province,total_count,total_area_kha,extraction_count,extraction_area_kha,exploration_count,exploration_area_kha
2026,6,Ulaanbaatar,170,14.1,166,13.9,4,0.2
```

### Mongolian (`mrpam-mining-permits-all-mn.csv`)
```
он,сар,аймаг,нийт_тоо,нийт_талбай_мян_га,ашиглалтын_тоо,ашиглалтын_талбай_мян_га,хайгуулын_тоо,хайгуулын_талбай_мян_га
2026,6,Улаанбаатар,170,14.1,166,13.9,4,0.2
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
- Licensed area values are already expressed in thousand hectares; do not
  multiply them by 1,000.
