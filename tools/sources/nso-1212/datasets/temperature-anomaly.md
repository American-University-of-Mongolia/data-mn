# Dataset: Ulaanbaatar Temperature Anomaly

- **ID**: `temperature-anomaly`
- **Parent**: `nso-temperature-by-station`
- **Table ID**: `DT_NSO_2400_022V2.px`
- **Category**: Environment
- **Frequency**: Monthly

## Transformation

Filter Ulaanbaatar observations to `Comparison with multi-year (1981-2010)`.
Normalize months to `YYYY-MM`, remove null values, and export bilingual
anomaly CSV and Excel files.

## Caveats

**2026-01 is wrong at the source** (verified 2026-09-28). NSO publishes January
2026 as a verbatim copy of March 2025, and the anomaly indicator is copied along
with the rest: the +2.6 °C shown for 2026-01 is *March 2025's* anomaly, not
January 2026's.

This one is dangerous precisely because it looks fine. Anomalies are small
numbers in every month, so a copied anomaly stays in-range and passes eyeball
review — and it will appear to corroborate the other temperature splits when it
is in fact the same corrupt record. Do not use this dataset to validate
2026-01 elsewhere. See Known Source Issues in `temperature-by-station.md`.
