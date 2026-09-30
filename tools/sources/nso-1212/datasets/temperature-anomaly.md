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

NSO occasionally publishes a corrupted anomaly cell (2008-11, 2016-03 and
2017-08 hold the month's minimum temperature or the baseline normal). The
transform (`repair_anomalies` in `tools/scripts/update_audited_nso_datasets.py`)
recomputes an anomaly as mean minus the calendar month's baseline normal when
the two disagree by more than 3 C and the mean itself is typical; when the
mean is the atypical value it keeps NSO's anomaly and prints a warning.
