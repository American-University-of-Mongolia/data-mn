# Dataset: Ulaanbaatar Temperature Extremes

- **ID**: `temperature-extremes-ulaanbaatar`
- **Parent**: `nso-temperature-by-station`
- **Table ID**: `DT_NSO_2400_022V2.px`
- **Category**: Environment
- **Frequency**: Monthly

## Transformation

Filter Ulaanbaatar observations to average, maximum, and minimum air
temperature. Normalize months to `YYYY-MM`, translate indicator labels, remove
null values, and export bilingual CSV and Excel files.

## Caveats

**2026-01 is wrong at the source** (verified 2026-09-28). NSO publishes January
2026 as a verbatim copy of March 2025, so all three indicators are March values:
average -4.1 °C, maximum 16.9 °C, minimum -17.1 °C. The maximum is the most
visibly impossible — +16.9 °C in a Ulaanbaatar January, against a 2005-2025
January maximum mean of -4.1 °C. Our values mirror the source faithfully;
re-fetching does not fix it. See Known Source Issues in
`temperature-by-station.md`.
