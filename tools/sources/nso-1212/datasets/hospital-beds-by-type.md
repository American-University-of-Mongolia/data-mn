# Hospital Beds by Department Type

**Dataset ID:** `hospital-beds-by-type`
**Source:** NSO 1212.mn
**Table ID:** DT_NSO_2100_005V1.px

## Description

Number of hospital beds across 9 department types in Mongolia for 2024. A snapshot view showing the distribution of hospital capacity by medical specialty.

## Data Structure

**Original table structure:**
- Indicators: Total, Internal medicine, Surgery and traumatology, Ophtalmology, Otolaryngology, Obstetrics, Gyneacology, Neurology, Psychiatry and narcology, Pediatrics, Beds per 1000 population
- Annual: 1989-2024

**Filter applied:**
- Year = 2024
- Exclude "Total" and "Beds per 1000 population" indicators
- Keep only the 9 department types

**Final structure:**
- Department (9 types)
- Hospital beds (count)

## API Path

- Sector: `Education, health`
- Subsector: `Births, deaths`
- Table: `DT_NSO_2100_005V1.px`

## MN Department Name Mappings

| English | Mongolian |
|---------|-----------|
| Internal medicine | Дотрын өвчин |
| Surgery and traumatology | Мэс засал, гэмтлийн |
| Ophtalmology | Нүдний |
| Otolaryngology | Чих, хамар, хоолойн |
| Obstetrics | Акушерийн |
| Gyneacology | Эхийн өвчний |
| Neurology | Мэдрэлийн |
| Psychiatry and narcology | Сэтгэцийн болон нарколог |
| Pediatrics | Хүүхдийн |

## Chart Specification

- Type: Horizontal bar chart
- X-axis: Hospital beds (quantitative, format ,d)
- Y-axis: Department name (nominal, sorted descending)
- Color: #3b82f6

## Update Frequency

Annual (updates typically available in Q4 of the same year)

## Notes

- 2024 data: Internal medicine leads with 7,564 beds out of 30,117 total
- Ophtalmology has fewest beds (183), reflecting specialized care model
