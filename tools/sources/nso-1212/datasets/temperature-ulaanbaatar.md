# Dataset: Ulaanbaatar Monthly Temperature

- **ID**: `temperature-ulaanbaatar`
- **Parent**: `nso-temperature-by-station`
- **Table ID**: `DT_NSO_2400_022V2.px`
- **Category**: Environment
- **Frequency**: Monthly

## Transformation

Filter the parent table to station `Ulaanbaatar` and indicator
`Average air temperature`. Normalize months to `YYYY-MM`, remove null values,
and export bilingual CSV and Excel files.

## Caveats

**2026-01 is wrong at the source** (verified 2026-09-28). NSO publishes January
2026 as a verbatim copy of March 2025, so this dataset reads -4.1 °C against a
2005-2025 January mean of -20.5 °C. Our value mirrors the source faithfully;
re-fetching does not fix it. See Known Source Issues in
`temperature-by-station.md`.
