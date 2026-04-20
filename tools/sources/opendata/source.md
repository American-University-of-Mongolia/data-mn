# opendata.gov.mn — Mongolia Open Data Portal

## Source Overview

| Field | Value |
|-------|-------|
| **Source ID** | `opendata` |
| **Name EN** | Mongolia Open Data Portal |
| **Name MN** | Нээлттэй өгөгдлийн нэгдсэн портал |
| **Operator** | Cabinet Secretariat (Засгийн газрын хэрэг эрхлэх газар) |
| **Portal URL** | https://opendata.gov.mn |
| **API Base** | https://opendata.gov.mn/api/v1 |
| **Data Type** | REST API (POST JSON) + file downloads |
| **Update Frequency** | Varies — daily to annual |
| **Language** | Mongolian only → translation required |
| **Total Datasets** | 6,613+ across 56+ organizations |
| **Launched** | 2020 (World Bank Smart Government Project) |

---

## API Discovery Notes

The portal is a Nuxt 3 SPA. The backend API was discovered by:
1. Reading `window.__NUXT__.config.public.mainURL` from the page HTML
2. Searching JS bundle `9d1zlazZ.js` for `$fetch(` calls
3. Reading `BYjc9lHE.js` JS chunk which constructs `${mainURL}/media/${path}`

**Runtime config (from HTML):**
```
mainURL: "https://opendata.gov.mn/api/v1"
```

All API calls use **POST with JSON body**. The SPA renders all routes server-side, so static HTML fetching returns the app shell only.

---

## API Endpoints

### `POST /api/v1/front/search`
Search and list datasets.

**Payload:**
```json
{
  "page": {"page": 1, "page_size": 20, "sort": "created_at DESC"},
  "org_reg_num": "",
  "data_uuid": "",
  "frequency_uuid": "",
  "start_term": "",
  "end_term": "",
  "query": "search terms"
}
```

**Response:**
```json
{
  "code": 200,
  "result": {
    "details": {
      "total_rows": 6613,
      "total_pages": 331,
      "items": [
        {
          "id": 6686,
          "name": "Хуулийн этгээдийн улсын бүртгэлийн нээлттэй өгөгдөл",
          "org": {"reg_num": "5296722", "name": "Улсын бүртгэлийн ерөнхий газар"},
          "frequency": {"name": "Өдөр бүр"},
          "term": "2026-04-19 08:00:00"
        }
      ]
    },
    "org_list": [...],
    "data_list": [...]
  }
}
```

### `POST /api/v1/front/reference`
Get data format types and update frequencies.

**Payload:** `{}` (empty)

**Returns:** `data_formats` (CSV, JSON, XML, XLSX, GeoJSON, ...) and `frequencies` UUIDs.

### `POST /api/v1/front/detail/view`
Get dataset metadata + file list.

**Payload:** `{"id": 6686}`

**Response key fields:**
- `id`, `name`, `description` — dataset metadata
- `org` — publishing organization
- `frequency` — update frequency
- `term` — last updated datetime
- `files` — array of downloadable files

### `POST /api/v1/front/detail/file/view`
Get metadata for a single file.

**Payload:** `{"id": 18132}` (file id from `files` array)

---

## File Download

Files are served via the API media endpoint (discovered in `BYjc9lHE.js`):
```
https://opendata.gov.mn/api/v1/media/{file.path}
```
The `ext` field determines file type but is NOT part of the URL — the server serves the binary directly. Note: the `/storage/{path}.{ext}` URL pattern returns the SPA HTML shell (confirmed false positive).

Example: `path = "20260419/65/6502bcae65267d1fbf6e360342df061e5eb0883a"` →
```
https://opendata.gov.mn/api/v1/media/20260419/65/6502bcae65267d1fbf6e360342df061e5eb0883a
```

Files can be CSV, JSON, XLSX, XML, or GeoJSON. Size ranges from KB to ~440 MB.

---

## High-Priority Datasets ("Holy Grail" from docs/vision.md)

| ID | Name | Org | Format | Size | Update |
|----|------|-----|--------|------|--------|
| 6686 | Хуулийн этгээдийн улсын бүртгэл | Улсын бүртгэлийн ерөнхий газар | JSON | ~440 MB | Daily |
| 6685 | Үл хөдлөх хөрөнгийн бүртгэл | Улсын бүртгэлийн ерөнхий газар | JSON | Large | Daily |
| 6681 | Иргэний бүртгэл | Улсын бүртгэлийн ерөнхий газар | JSON | Large | Daily |

---

## Key Organizations

| Org Name (MN) | Reg Num | Domain |
|--------------|---------|--------|
| Улсын бүртгэлийн ерөнхий газар | 5296722 | Legal Entity, Real Estate, Citizen registries |
| Нийгмийн даатгалын ерөнхий газар | — | Pension, social insurance stats |
| Цагдаагийн ерөнхий газар | — | Crime statistics |
| Гааль, татварын ерөнхий газар | — | Customs, tax data |
| Статистикийн хороо | — | Overlaps with NSO 1212.mn |

---

## Skill Location

`.claude/skills/datamn-source-opendata/`

| File | Purpose |
|------|---------|
| `SKILL.md` | Full usage docs |
| `query_api.py` | Search and browse datasets |
| `fetch_data.py` | Download by ID, convert to CSV |

---

## Data Format Notes

- **JSON**: Most large datasets (registries). May be array of objects or wrapped in `{"data": [...]}`.
- **CSV**: Smaller datasets, ready to use directly.
- **XLSX**: Some periodic reports. Openpyxl can read these.
- **GeoJSON**: Geographic datasets (land parcels, administrative boundaries).

Large JSON files (>100 MB): use streaming with `ijson` or process in chunks.

---

## Language and Translation

All datasets are **Mongolian only**. Both column names and categorical values must be translated.

Use `tools/scripts/translate_csv.py`:
```bash
conda run -n datamn python3 tools/scripts/translate_csv.py \
  dataset-mn.csv --from mn --to en -o dataset-en.csv
```

See `tools/TRANSLATION_GUIDE.md` for complete workflow.
