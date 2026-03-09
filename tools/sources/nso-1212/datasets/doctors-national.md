# doctors-national

**Dataset ID**: `doctors-national`
**Source**: National Statistics Office of Mongolia (1212.mn)
**Table**: `DT_NSO_0100_01TTT08.px`
**Title**: NUMBER OF DOCTORS
**Sector**: Historical data
**Subsector**: Health protection
**Last Updated**: 2025-02-04T09:10:20
**Frequency**: Annual

## Variables

### Category (2) — 4 values
| Value | EN | MN |
|-------|----|----|
| 0 | Total number of doctors | Их эмчийн тоо, бүгд |
| 1 | Women doctors, total | Эмэгтэй |
| 2 | As percentage of total number of doctors | Бүх эмч нарт эмэгтэй эмч нарын эзлэх хувь |
| 3 | Number of doctors per 10,000 of the population | 10 000 хүн ам тутамд ногдох их эмч |

### Time (Annual) — 42 values
Years: 1925, 1930, 1940, 1947, 1950, 1952, 1955, 1957, 1958, 1960–1992 (annual)

## Scope (doctors-national)

- **Category filter**: `0` (Total number of doctors) — national total only
- **Columns EN**: `year`, `doctors_total`
- **Columns MN**: `он`, `эмч_тоо_нийт`
- **Rows**: 42 annual observations
- **Date range**: 1925–1992

## API Fetch

```
POST https://data.1212.mn/api/v1/{lang}/NSO/Historical%20data/Health%20protection/DT_NSO_0100_01TTT08.px

Body:
{
  "query": [
    {"code": "Ангилал", "selection": {"filter": "item", "values": ["0"]}},
    {"code": "он", "selection": {"filter": "item", "values": ["0","1",...,"41"]}}
  ],
  "response": {"format": "json"}
}
```
