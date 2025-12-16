# Dataset: Average Air Temperature by Station

## Identification

- **ID**: `nso-temperature-by-station`
- **Source**: `nso-1212`
- **Category**: Environment
- **Tags**: [temperature, climate, weather, environment, stations]

## Source Reference

- **Table ID**: `DT_NSO_2400_022V2.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Environment`
- **API Path**: `/en/NSO/Economy, environment/Environment/DT_NSO_2400_022V2.px`

## Title

- **EN**: Average Air Temperature by Station Location and Month
- **MN**: Агаарын дундаж температур, станцын байршил, сараар

## Description

Monthly air temperature data from 28 weather stations across Mongolia, from 2005 to present. Includes average temperature, minimum and maximum temperatures, and comparison to the 1981-2010 baseline period. Provides comprehensive climate monitoring data covering all major regions of Mongolia.

## Variables

### Indicator (Үзүүлэлт)
- `Average air temperature`: Monthly mean temperature (°C)
- `Comparison with multi-year (1981-2010)`: Temperature anomaly from baseline
- `Maximum temperature`: Monthly maximum (°C)
- `Minimum temperature`: Monthly minimum (°C)

### Station location (Станцын байршил)
Weather stations across Mongolia:

**West Region:**
- Altai, Ulgii, Ulaangom, Khovd, Uliastai, Tosontsengel

**Khangai Region:**
- Arvaikheer, Bayankhongor, Bulgan, Murun, Kharkhorin, Khatgal, Tsetserleg, Erdenet

**Central Region:**
- Ulaanbaatar, Baruunkharaa, Darkhan, Zuunmod, Zuunkharaa

**East Region:**
- Baruun-Urt, Undurkhaan, Choibalsan, Sukhbaatar

**Gobi Region:**
- Dalanzadgad, Mandalgovi, Zamiin-Uud, Sainshand, Khanbogd, Choir

### Month (Сар)
Monthly data from January 2005 to present (YYYY-MM format)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/Environment/
   ```

2. Find `DT_NSO_2400_022V2.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2400_022V2.px --lang both --output ./output
```

### Validation

- Temperature values should be within reasonable range (-50°C to +45°C)
- All months should have complete station coverage
- Anomaly values should be small (typically -5 to +5°C range)

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. temperature-ulaanbaatar

- **ID**: `temperature-ulaanbaatar`
- **Title EN**: Ulaanbaatar Monthly Temperature (2005-2025)
- **Title MN**: Улаанбаатар хотын сарын дундаж температур (2005-2025)
- **Filter**:
  - Station location: Ulaanbaatar
  - Indicator: Average air temperature
- **Chart Type**: line
- **Chart Config**:
  - X-axis: month (temporal)
  - Y-axis: value (temperature in °C)
  - Color: #3b82f6 (blue)
- **Description EN**: Monthly average air temperature in Ulaanbaatar from 2005 to present.
- **Description MN**: Улаанбаатар хотын сарын дундаж агаарын температур 2005 оноос хойш.
- **Key Findings**:
  - Coldest month on record
  - Warmest month on record
  - Annual temperature range

### 2. temperature-seasonal-average

- **ID**: `temperature-regional`
- **Title EN**: Mongolia Temperature by Region (2005-2025)
- **Title MN**: Монгол Улсын температур бүс нутгаар (2005-2025)
- **Filter**:
  - Indicator: Average air temperature
  - Station location: Ulaanbaatar, Darkhan, Dalanzadgad, Choibalsan, Khovd (5 representative stations)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: month (temporal)
  - Y-axis: value (temperature in °C)
  - Color: station location (categorical)
- **Description EN**: Comparison of temperature patterns across Mongolia's major regions.
- **Description MN**: Монгол Улсын томоохон бүс нутгуудын температурын харьцуулалт.
- **Key Findings**:
  - Warmest region
  - Coldest region
  - Seasonal variation differences

### 3. temperature-extremes-ulaanbaatar

- **ID**: `temperature-extremes-ulaanbaatar`
- **Title EN**: Ulaanbaatar Temperature Extremes (2005-2025)
- **Title MN**: Улаанбаатар хотын температурын хэт утга (2005-2025)
- **Filter**:
  - Station location: Ulaanbaatar
  - Indicator: Average air temperature, Maximum temperature, Minimum temperature
- **Chart Type**: range-area or multi-line
- **Chart Config**:
  - X-axis: month (temporal)
  - Y-axis: value (temperature in °C)
  - Color by indicator: Average=#3b82f6, Max=#ef4444, Min=#06b6d4
- **Description EN**: Average, minimum, and maximum monthly temperatures in Ulaanbaatar.
- **Description MN**: Улаанбаатар хотын сарын дундаж, хамгийн бага, хамгийн их температур.
- **Key Findings**:
  - Temperature range (max - min)
  - Coldest recorded temperature
  - Hottest recorded temperature

### 4. temperature-anomaly

- **ID**: `temperature-anomaly`
- **Title EN**: Mongolia Temperature Anomaly vs 1981-2010 Baseline
- **Title MN**: Монгол Улсын температурын хазайлт 1981-2010 суурь утгаас
- **Filter**:
  - Indicator: Comparison with multi-year (1981-2010)
  - Station location: Ulaanbaatar (national representation)
- **Chart Type**: area (with zero baseline)
- **Chart Config**:
  - X-axis: month (temporal)
  - Y-axis: value (temperature deviation in °C)
  - Color: conditional (positive=#ef4444, negative=#3b82f6)
- **Description EN**: How current temperatures compare to the 1981-2010 historical average.
- **Description MN**: Одоогийн температур 1981-2010 оны түүхэн дунджаас хэрхэн ялгаатай байгаа.
- **Key Findings**:
  - Overall trend (warming/cooling)
  - Percentage of months above baseline
  - Largest positive anomaly

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest values
- Extreme values (min/max)
- Trend direction

### Common Tags
- mongolia
- temperature
- climate
- weather
- environment
- nso

### Excerpt Templates

**temperature-ulaanbaatar**:
- EN: "Ulaanbaatar's monthly average temperature ranges from {min_temp}°C in January to {max_temp}°C in July."
- MN: "Улаанбаатар хотын сарын дундаж температур 1-р сарын {min_temp}°C-ээс 7-р сарын {max_temp}°C хүртэл хэлбэлздэг."

**temperature-regional**:
- EN: "Temperature comparison across 5 major weather stations in Mongolia from 2005 to {latest_year}."
- MN: "Монгол Улсын 5 үндсэн цаг уурын станцын температурын харьцуулалт, 2005-{latest_year}."

**temperature-extremes-ulaanbaatar**:
- EN: "Ulaanbaatar recorded a minimum of {coldest}°C and maximum of {hottest}°C between 2005 and {latest_year}."
- MN: "Улаанбаатар хотод 2005-{latest_year} оны хооронд хамгийн бага {coldest}°C, хамгийн их {hottest}°C температур бүртгэгдсэн."

**temperature-anomaly**:
- EN: "{percent_above}% of months since 2005 have been warmer than the 1981-2010 average in Ulaanbaatar."
- MN: "2005 оноос хойш Улаанбаатарт {percent_above}% сар 1981-2010 оны дунджаас дулаан байсан."

## Notes

- Temperature data has high coverage (28 stations, monthly updates)
- Regional aggregates (West region, Central region, etc.) have minimal data - use individual stations
- Some months may have missing values due to equipment issues
- **Parent dataset**: This dataset stores the raw data; only the splits are published to data.mn
