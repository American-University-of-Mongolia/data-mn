# air-pollution-concentration

**Dataset ID**: `air-pollution-concentration`
**Source**: National Statistics Office of Mongolia (1212.mn)
**Path**: Economy, environment → Environment → CONCENTRATION OF AIR POLLUTION, by location, by month
**Tables** (TABLE SWITCH 2026-10-12, source updated 2026-10-08):
- `DT_NSO_2400_015V1.px` — SULPHUR DIOXIDE, by location, by month (ХҮХЭРЛЭГ ХИЙ, станцын байршил, сараар)
- `DT_NSO_2400_015V4.px` — PARTICULATE MATTER PM10, by location, by month
- `DT_NSO_2400_015V5.px` — PARTICULATE MATTER PM2.5, by location, by month
**Frequency**: Monthly
**Build script**: `tools/scripts/build_air_pollution_concentration.py --version N [--fetch] [--apply]`,
then `tools/scripts/rebuild_downloads.py --dataset air-pollution-concentration --apply`

**Table IDs are reused.** Inside the folder: V1=SO₂, V2=NO₂, V3=CO, V4=PM10,
V5=PM2.5, V6=O₃. Directly under Environment, `DT_NSO_2400_015V3.px` is an
older SO₂ table (43 locations, old station names, used for v2) and
`DT_NSO_2400_015V4.px` is a land-territory table. Always fetch by the full
folder path.

## Variables

### Indicator
- Selected: Average concentration only (dropped Maximum, "MN by day" = number
  of measurements / Хэмжилтийн тоо, Exceeding % of AQS)

### Station location — 48 total, 17 UB stations selected
UB stations (NSO names as of Oct 2026; old names in brackets):
Misheel-Expo center, West crossroad, Takhilt, 1st micro district [1st micro district],
13th micro district, 100 Ail, 32 Toirog [32nd Toirog], Ofitseruudiin ordon,
Tsakhilgaan stants, khar khorin zakh [Kharkhorin market] (PM tables spell it
"kharkhorin"), Urgakh naran micro district, Dambadarjaa [Dambdarjaa], Khailaast,
Nisekh, Tolgoit, Zuragt, Amgalan, Bayankhoshuu, 248nd tsetserleg [248th
kindergarten], Bogd khan palace museum.

Excluded: UB stations added 2026-01 (Yarmag, Nalaikh, Sharkhad, 5 Buudal) — kept
out so the station set stays fixed. Revisit if they build a longer record.

## Method

For each pollutant and month: unweighted mean of the station "Average" values
of the 17 stations that have data, rounded to 4 dp. No interpolation; a month
with no reporting station stays blank (PM10 2009-04, PM2.5 2010-08). Station
coverage changes a lot: before 2015, 2–8 stations for SO₂ and at most 2 for
PM2.5; from 2015, 4–15. No month has all 17. The MDX pages carry a methodology
note saying this. Update its numbers on every refresh.

## Scope

- **3 pollutants**: PM2.5 (2010-07 →), PM10 (2008-12 →), SO₂ (2002-02 →)
- **Geography**: Ulaanbaatar only
- **Columns EN**: `month`, `pollutant`, `value_mg_m3` (pollutant: PM2.5, PM10, SO2)
- **Columns MN**: `сар`, `бохирдуулагч`, `утга_мг_м3` (Тоосонцор PM2.5, Тоосонцор PM10, Хүхэрлэг хий SO₂)
- **Format**: Long form, 704 rows (v3)
- **Unit**: mg/m³
- **Date range**: 2002-02 to 2026-09

## Data quality checks

- NSO published PM2.5 for 2026-09 as an exact copy of PM10 at every station.
  The build drops any PM2.5 month where all (≥3) station values equal PM10.
- SO₂ 2002-01 has no UB station values in the folder table (the old table had
  3), so SO₂ starts 2002-02 from v3.
- Overlapping months matched v1 (PM) and v2 (SO₂) exactly at the v3 switch.
- A few station-months have PM2.5 > PM10 (16 as of 2026-10); left as published.

## Notes

- Strong seasonal pattern: very high in winter (Nov–Feb), much lower in summer
- Also available: `DT_NSO_2024_135V01.px` — annual concentrations by station
