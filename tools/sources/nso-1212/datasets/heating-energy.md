# heating-energy

## Source Table

- **Table ID:** DT_NSO_1100_011V1.px
- **Title:** BALANCE OF THERMAL ENERGY, by year
- **Sector:** Industry, service → Industry
- **API URL:** `https://data.1212.mn/api/v1/{lang}/NSO/Industry,%20service/Industry/DT_NSO_1100_011V1.px`

## Variables

| Variable | Values |
|----------|--------|
| Indicators | 9 (Gross generation, Station internal use, Distribution total, Industry & construction, Transport & communication, Agriculture, Household & communal housing, Other, Transmission losses) |
| Year | 30 (1995-2024) |

## Split Filter

The chart split uses 3 key balance indicators:
- **Gross generation** — total thermal energy produced
- **Distribution total** — total distributed to establishments and households
- **Transmission losses** — energy lost during distribution

Values are in thousand Gcal.

## Update Instructions

1. Fetch data: `python3 fetch_data.py --table DT_NSO_1100_011V1.px --output /tmp/nso-heating`
2. Filter to the 3 split indicators from EN source
3. Build both EN and MN CSVs from single EN source with consistent order
4. Regenerate XLSX in wide format
