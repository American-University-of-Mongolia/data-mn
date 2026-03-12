# crop-production-by-type

**Dataset ID**: `crop-production-by-type`
**Source**: National Statistics Office of Mongolia (1212.mn)
**Table**: `DT_NSO_0100_01T013.px`
**Title**: CROSS HARVEST OF CROP PRODUCTION, by type and by year
**Sector**: Historical data
**Subsector**: Agriculture
**Last Updated**: 2025-12-30T16:05:49
**Frequency**: Annual

## Variables

### Type — 7 values
| Code | EN | MN |
|------|----|----|
| 0 | Cereals | Үр тариа-бүгд |
| 1 | Wheat | Буудай |
| 2 | Barley | Арвай |
| 3 | Oats | Овъёос |
| 4 | Potatoes | Төмс |
| 5 | Vegetables | Хүнсний ногоо |
| 6 | Fodder crops | Тэжээлийн ургамал |

### Year — 40 values
Years: 1941, 1943, 1952–1970 (with gaps), 1970–1992 (annual)

## Scope (crop-production-by-type)

- **All 7 crop types** included (national gross production, not regional)
- **Columns EN**: `year`, `crop_type`, `production_thousand_tonnes`
- **Columns MN**: `он`, `таримлын_төрөл`, `ургац_мянган_тонн`
- **Format**: Long form (280 rows = 7 types × 40 years)
- **Unit**: Thousand tonnes
- **Date range**: 1941–1992

## API Fetch

```
POST https://data.1212.mn/api/v1/{lang}/NSO/Historical%20data/Agriculture/DT_NSO_0100_01T013.px

Body:
{
  "query": [
    {"code": "Төрөл", "selection": {"filter": "item", "values": ["0","1","2","3","4","5","6"]}},
    {"code": "Он", "selection": {"filter": "item", "values": ["0","1",...,"39"]}}
  ],
  "response": {"format": "json"}
}
```

## Notes

- "Cereals" (code 0) is the aggregate of Wheat + Barley + Oats
- Some early years (1941, 1943) have missing values for some crop types
- National scope only — no regional breakdown in this table
