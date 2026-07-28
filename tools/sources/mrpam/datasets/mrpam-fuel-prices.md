# mrpam-fuel-prices

Monthly retail fuel prices by province and city from MRPAM Table 4.6.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-fuel-prices` |
| **Source** | `mrpam` |
| **Source Table** | 4.6 |
| **Update Frequency** | Monthly |
| **Units** | MNT per liter (төгрөг/литр) |

## Description

Retail prices for AI-92, AI-92 Euro-5, AI-95, diesel, and diesel Euro-5
across Mongolia's aimags and cities. Full downloads retain every extracted
geography and grade. The chart shows arithmetic national averages calculated
from the available geography rows for each report month.

## CSV Schema

### English (`mrpam-fuel-prices-en.csv`)
```
year,month,province,ai92_price,ai92_euro5_price,ai95_price,diesel_price,diesel_euro5_price
2026,6,Arkhangai,2700,3180,3740,3560,4150
```

### Mongolian (`mrpam-fuel-prices-mn.csv`)
```
он,сар,аймаг,аи92_үнэ,аи92_евро5_үнэ,аи95_үнэ,дизель_үнэ,дизель_евро5_үнэ
2026,6,Архангай,2700,3180,3740,3560,4150
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-fuel-prices --year 2026
```

## Section Keywords

Search for the exact heading prefix:
`4.6. ГАЗРЫН ТОСНЫ БҮТЭЭГДЭХҮҮНИЙ ЖИЖИГЛЭН`.

## Notes

- The unit is MNT per liter.
- Empty cells and hyphens remain missing; they must not be converted to zero.
- A monthly history is assembled by extracting Table 4.6 from each report.
- Chart CSVs contain national averages for five grades; `-all-` downloads
  contain all extracted province and city rows.
- The cached August 2023 report is English and does not match the Mongolian
  extraction contract, so that month is not included in version 1.
