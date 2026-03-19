# telecommunications-national

**Dataset ID**: `telecommunications-national`
**Source**: National Statistics Office of Mongolia (1212.mn)
**Table**: `DT_NSO_0100_01T37.px` — MAIN INDICATORS OF TELECOMMUNICATIONS, by year
**Sector**: Historical data
**Subsector**: Transport and communication
**Last Updated**: 2025-10-08
**Frequency**: Annual (historical series, unlikely to extend)

## Variables

### Indicator — 12 total
1. Post offices (count)
2. Telegraph stations (count)
3. Telephone exchanges (count)
4. Telegraph and telephone lines (thousand km)
5. Telephone points (thousands)
6. Radio stations (count)
7. Radio nodes (count)
8. Radio concentration points (count)
9. Radio points (thousands)
10. Receivers (thousands)
11. Televisions (thousands)
12. TV transmission and retransmission stations (count)

### Year — 40 values
Range: 1940 to 1992 (not all years present for all indicators)

## Scope (telecommunications-national)

- **12 indicators**: All indicators from the source table
- **Geography**: National (Mongolia)
- **Columns EN**: `year`, `indicator`, `unit`, `value`
- **Columns MN**: `он`, `үзүүлэлт`, `хэмжих_нэгж`, `утга`
- **Format**: Long form (264 rows — nulls dropped)
- **Units**: count, thousand km, or thousands (per indicator)
- **Date range**: 1940 to 1992

## Notes

- Source has 480 rows (12 indicators × 40 years); 264 are non-null
- The 1950 value for "Telephone points" (3600 thousand) is a data anomaly and has been excluded
- Data covers the socialist era; the series ends at 1992 with Mongolia's transition
- Chart shows only "thousands" unit indicators for comparability: Telephone points, Radio points, Receivers, Televisions
