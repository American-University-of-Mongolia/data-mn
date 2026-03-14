# air-pollution-concentration

**Dataset ID**: `air-pollution-concentration`
**Source**: National Statistics Office of Mongolia (1212.mn)
**Tables**:
- `DT_NSO_2400_015V4.px` — PARTICULATE MATTER PM10, by location, by month
- `DT_NSO_2400_015V5.px` — PARTICULATE MATTER PM2.5, by location, by month
**Sector**: Economy, environment
**Subsector**: Environment → CONCENTRATION OF AIR POLLUTION, by location, by month
**Last Updated**: 2026-03-10
**Frequency**: Monthly

## Variables

### Indicator
- Selected: Average concentration only (dropped Maximum, MN by day, Exceeding %)

### Station location — 43 total, 17 UB stations selected
UB stations: Misheel-Expo center, West crossroad, 1st micro district, 13th micro district,
32nd Toirog, Ofitseruudiin ordon, Kharkhorin market, Urgakh naran micro district,
Dambdarjaa, Khailaast, Nisekh, Tolgoit, Zuragt, Amgalan, Bayankhoshuu,
248th kindergarten, Bogd khan palace museum

### Month — 290 values
Range: 2002-01 to 2026-02

## Scope (air-pollution-concentration)

- **2 pollutants**: PM2.5 and PM10 (most health-critical for Ulaanbaatar)
- **Geography**: Ulaanbaatar only (17 stations averaged per month)
- **Columns EN**: `month`, `pollutant`, `value_mg_m3`
- **Columns MN**: `сар`, `бохирдуулагч`, `утга_мг_м3`
- **Format**: Long form (580 rows = 290 months × 2 pollutants)
- **Unit**: mg/m³
- **Date range**: 2002-01 to 2026-02

## Notes

- Values are monthly averages across all available UB monitoring stations
- WHO annual guideline for PM2.5: 0.005 mg/m³; UB peak reached 0.622 mg/m³
- Strong seasonal pattern: very high in winter (Nov-Feb), much lower in summer
- The subfolder "CONCENTRATION OF AIR POLLUTION, by location, by month" contains 6 separate tables (SO2=V1, NO2=V2, CO=V3, PM10=V4, PM2.5=V5, Ozone=V6)
- Also available: `DT_NSO_2024_135V01.px` — annual concentrations by station
