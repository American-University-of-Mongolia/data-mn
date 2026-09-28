# Dataset: Mongolia Temperature by Region

- **ID**: `temperature-regional`
- **Parent**: `nso-temperature-by-station`
- **Table ID**: `DT_NSO_2400_022V2.px`
- **Category**: Environment
- **Frequency**: Monthly

## Transformation

Filter average air temperature to Ulaanbaatar, Darkhan, Dalanzadgad,
Choibalsan, and Khovd. Normalize months to `YYYY-MM`, remove null values, and
export bilingual station-level CSV and Excel files.

## Caveats

**2026-01 is wrong at the source** (verified 2026-09-28). NSO publishes January
2026 as a verbatim copy of March 2025, so all 5 stations read 13-21 °C warmer
than a normal January (Ulaanbaatar -4.1 °C against a 2005-2025 January mean of
-20.5 °C). Our values mirror the source faithfully; re-fetching does not fix it.
See Known Source Issues in `temperature-by-station.md`.
