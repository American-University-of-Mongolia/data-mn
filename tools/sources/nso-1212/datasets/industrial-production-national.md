# industrial-production-national

**Dataset ID**: `industrial-production-national`
**Source**: National Statistics Office of Mongolia (1212.mn)
**Table**: `DT_NSO_1100_013V1.px`
**Title**: PRODUCTION OF MAJOR COMMODITIES, by year
**Sector**: Industry, service
**Subsector**: Industry
**Last Updated**: 2025-09-30T10:35:46
**Frequency**: Annual

## Variables

### Commodities — 74 values (7 selected)
| Code | EN | MN | Unit |
|------|----|----|------|
| selected | Coal | Нүүрс | thousand tonnes |
| selected | Copper concentrate (35%) | Зэсийн баяжмал (35%) | thousand tonnes |
| selected | Gold | Алт | kg |
| selected | Electricity | Цахилгаан эрчим хүч | million kWh |
| selected | Crude oil | Газрын тос | thousand barrels |
| selected | Iron ore | Төмрийн хүдэр | thousand tonnes |
| selected | Molybdenum concentrate (47%) | Молибдений баяжмал (47%) | tonnes |

### Year — 36 values
Years: 1989–2024

## Scope (industrial-production-national)

- **7 key industrial commodities** selected from 74 in the source table
- **Columns EN**: `year`, `commodity`, `unit`, `value`
- **Columns MN**: `он`, `бараа_бүтээгдэхүүн`, `хэмжих_нэгж`, `утга`
- **Format**: Long form (226 rows after dropping NaN)
- **Units**: Vary per commodity (see table above)
- **Date range**: 1989–2024

## Notes

- Units differ per commodity — a `unit` column is included in the CSV for clarity
- Crude oil: 9 missing values (years with no production)
- Gold: 2 missing values (early years)
- Iron ore: 15 missing values (early years before large-scale mining)
- 74 commodities available in source; only 7 strategic ones included
- Source last updated: 2025-09-30
