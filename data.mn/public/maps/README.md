# Map boundary files

## mongolia-aimags.json

Mongolia first-level administrative boundaries (21 aimags + Ulaanbaatar),
used by choropleth charts via Vega-Lite `geoshape` + `lookup` join.

- **Source**: geoBoundaries `gbOpen` MNG ADM1 (boundary ID `MNG-ADM1-14279143`,
  built from OpenStreetMap + Wambacher, fetched 2026-09-08)
- **Upstream URL**:
  `https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/MNG/ADM1/geoBoundaries-MNG-ADM1_simplified.geojson`
- **License**: Open Data Commons Open Database License (ODbL) 1.0 —
  © geoBoundaries / OpenStreetMap contributors. Keep this attribution
  when redistributing.
- **Processing**: stripped upstream properties, renamed `shapeName` values to
  data.mn canonical English region names, added `name_mn` (Mongolian names),
  rounded coordinates to 3 decimals, and reversed all ring winding orders
  (upstream rings are counter-clockwise; Vega/d3 fills them inverted —
  clockwise winding renders correctly).

Each feature has exactly two properties:

- `name` — English name, matches the `region` column of `-en.csv` files
- `name_mn` — Mongolian name, matches the `бүс` column of `-mn.csv` files

Name mapping applied (upstream → data.mn):

| Upstream shapeName | name | name_mn |
|---|---|---|
| Arkhangai | Arkhangai | Архангай |
| Bayan-Ölgii | Bayan-Ulgii | Баян-Өлгий |
| Bayankhongor | Bayankhongor | Баянхонгор |
| Bulgan | Bulgan | Булган |
| Darkhan-Uul | Darkhan-Uul | Дархан-Уул |
| Dornod | Dornod | Дорнод |
| Dornogovi | Dornogovi | Дорноговь |
| Dundgovi | Dundgovi | Дундговь |
| Govi-Altai | Govi-Altai | Говь-Алтай |
| Govisumber | Govisumber | Говьсүмбэр |
| Hovsgel | Khuvsgul | Хөвсгөл |
| Khentii | Khentii | Хэнтий |
| Khovd | Khovd | Ховд |
| Orkhon | Orkhon | Орхон |
| Selenge | Selenge | Сэлэнгэ |
| Sükhbaatar | Sukhbaatar | Сүхбаатар |
| Töv | Tuv | Төв |
| Ulaanbaatar | Ulaanbaatar | Улаанбаатар |
| Uvs | Uvs | Увс |
| Zavkhan | Zavkhan | Завхан |
| Ömnögovi | Umnugovi | Өмнөговь |
| Övörkhangai | Uvurkhangai | Өвөрхангай |
