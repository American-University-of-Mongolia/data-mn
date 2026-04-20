---
name: datamn-source-opendata
description: Query Mongolia's unified open data portal (opendata.gov.mn) — 6,613+ datasets from 56+ government organizations including Legal Entity Registry, Real Estate Registry, citizen records, police, and social insurance data. Use when adding datasets from any Mongolian government ministry or agency.
dependencies:
  - python3
  - requests
  - pandas
  - openpyxl
---

# opendata.gov.mn Data Source Skill

Queries the Cabinet Secretariat's unified open data portal (World Bank-funded, launched 2020) and produces bilingual CSVs ready for the data.mn pipeline.

Base directory for this skill (repo-relative): `.claude/skills/datamn-source-opendata`

---

## Source Overview

| Field | Value |
|-------|-------|
| **Source ID** | `opendata` |
| **Name EN** | Mongolia Open Data Portal |
| **Name MN** | Нээлттэй өгөгдлийн нэгдсэн портал |
| **Base URL** | https://opendata.gov.mn |
| **API Base** | https://opendata.gov.mn/api/v1 |
| **Data Type** | REST API (POST JSON) |
| **Update Frequency** | Varies (daily, weekly, monthly, annual) |
| **Language** | Mongolian only — translation required |
| **Total Datasets** | 6,613+ across 56+ organizations |

---

## API Reference

The portal is a Nuxt SPA with a backend REST API. **All endpoints use POST with JSON body.**

### Runtime Config
Discovered from `window.__NUXT__.config`:
```
mainURL: "https://opendata.gov.mn/api/v1"
```

### Endpoints

| Endpoint | Purpose | Key Payload Fields |
|----------|---------|-------------------|
| `POST /front/search` | List/search datasets | `page`, `query`, `org_reg_num`, `data_uuid`, `frequency_uuid` |
| `POST /front/reference` | Get format types and frequencies | `{}` (empty) |
| `POST /front/detail/view` | Get dataset metadata + file list | `id` (integer) |
| `POST /front/detail/file/view` | Get single file metadata | `id` (file integer id) |

### Download URL Pattern
Files are served at:
```
https://opendata.gov.mn/storage/{path}.{ext}
```
Where `path` and `ext` come from the file object in `/front/detail/view`.

### Search Payload Example
```json
{
  "page": {"page": 1, "page_size": 20, "sort": "created_at DESC"},
  "org_reg_num": "",
  "data_uuid": "",
  "frequency_uuid": "",
  "start_term": "",
  "end_term": "",
  "query": "хуулийн этгээд"
}
```

### Search Response Structure
```json
{
  "code": 200,
  "result": {
    "details": {
      "total_rows": 6613,
      "total_pages": 331,
      "items": [{"id": 6686, "name": "...", "org": {...}, "frequency": {...}}]
    },
    "org_list": [...],
    "data_list": [...]
  }
}
```

---

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `query_api.py` | Search and browse datasets; list by org or keyword |
| `fetch_data.py` | Download a dataset by ID to CSV |

---

## Workflow

### Step 1: Search for Datasets

```bash
cd .claude/skills/datamn-source-opendata

# Search by keyword
conda run -n datamn python3 query_api.py хүн ам

# Search in English (translates automatically)
conda run -n datamn python3 query_api.py population

# List all datasets (paginated)
conda run -n datamn python3 query_api.py --list --page 1

# Get dataset detail by ID
conda run -n datamn python3 query_api.py --detail 6686

# List datasets from a specific org (by reg_num)
conda run -n datamn python3 query_api.py --org 5296722
```

### Step 2: Download Dataset

```bash
# Download dataset ID 6686 to tools/temp/opendata/
conda run -n datamn python3 fetch_data.py 6686

# Download and auto-convert to CSV
conda run -n datamn python3 fetch_data.py 6686 --format csv

# Output goes to: tools/temp/opendata/{id}/
```

### Step 3: Translate to English

```bash
# Translate Mongolian CSV to English
conda run -n datamn python3 tools/scripts/translate_csv.py \
  tools/temp/opendata/6686/dataset-mn.csv \
  --from mn --to en \
  -o tools/temp/opendata/6686/dataset-en.csv
```

---

## High-Priority Datasets ("Holy Grail")

| Dataset ID | Name MN | Category | Update |
|-----------|---------|---------|--------|
| 6686 | Хуулийн этгээдийн улсын бүртгэл | Legal Entity Registry | Daily |
| 6685 | Үл хөдлөх хөрөнгийн бүртгэл | Real Estate Registry | Daily |
| 6681 | Иргэний бүртгэл | Citizen Registry | Daily |

---

## Key Organizations

| Org Name | Reg Num | Notable Datasets |
|----------|---------|-----------------|
| Улсын бүртгэлийн ерөнхий газар | 5296722 | Legal Entity, Real Estate, Citizen registries |
| Нийгмийн даатгалын ерөнхий газар | — | Pension, social insurance |
| Цагдаагийн ерөнхий газар | — | Crime statistics |

---

## Data Format Notes

- Most datasets are **JSON** with Mongolian field names
- Some datasets have **CSV** or **XLSX** files
- File size varies widely: small datasets (~KB) to large registry exports (~GB)
- The Legal Entity Registry JSON is ~440 MB — use streaming download

---

## Language Support

**Source Language**: Mongolian only  
**Translation Required**: Yes — all column names and categorical values must be translated

### Common Column Translations

| Mongolian | English |
|-----------|---------|
| Регистрийн дугаар | registration_number |
| Оноосон нэр | name |
| Бүртгэсэн огноо | registration_date |
| Хэлбэр | type |
| Төрөл | category |
| Хуулийн этгээдийн хаяг | address |
| Үйл ажиллагааны чиглэл | activity |
| Хүйс | sex |
| Эцэг/эх/-ийн нэр | parent_name |
| Нэр | given_name |
| Төлөв | status |

### Province Name Translations (from NSO standard)

| Mongolian | English |
|-----------|---------|
| Улаанбаатар | Ulaanbaatar |
| Архангай | Arkhangai |
| Баян-Өлгий | Bayan-Olgii |
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
| Төв | Tov |
| Увс | Uvs |
| Ховд | Khovd |
| Хөвсгөл | Khuvsgul |
| Хэнтий | Khentii |

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| 440 MB JSON too large to load in pandas | Use `pd.read_json(path, lines=True)` or stream with `ijson` |
| Dataset has no CSV/XLSX file | Download JSON and convert with `pd.json_normalize()` |
| Nested JSON fields | Flatten with `pd.json_normalize(df['field'])` |
| Rate limiting | Add `time.sleep(1)` between requests |
| Large file OOM | Process in chunks with `chunksize` parameter |

---

## Dependencies

All included in `datamn` conda environment:
```
requests>=2.31.0
pandas>=2.0.0
openpyxl>=3.1.0
```
