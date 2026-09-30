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

## Source Data Cleaning

NSO table `DT_NSO_2400_022V2` contains corrupted cells. The transform
(`clean_temperature_table` in `tools/scripts/update_audited_nso_datasets.py`)
runs before any split is written and prints every change:

- **Copied months are dropped.** 2026-01 repeats 2025-03 for every station
  and indicator; it is omitted until NSO corrects it.
- **Misplaced anomalies are recomputed** as mean minus the normal (NSO's
  normal for that calendar month in nearby years). This happens only when the
  anomaly cell holds the month's min/max, the normal, or 0.0. Examples:
  2008-11 and 2016-03 at all stations, and Ulaanbaatar 2017-08.
- **Outlier means are recomputed** as normal plus anomaly, but only when one
  station is off relative to the others that month (Ulaanbaatar 2009-07:
  25.1 -> 19.3 C). A flipped sign is also fixed (Baruun-Urt 2016-12).
- **Impossible or misplaced extremes are dropped.** A maximum below the
  mean, a minimum above it, or an atypical value equal to the month's anomaly
  is removed; it can't be reconstructed. 2023-06 has the anomaly in the
  maximum column and 2023-07 in the minimum column, at nearly every station.
- **Everything else is left unchanged with a warning.** For example, months
  where several stations shift together, which looks like a baseline change
  or real weather.

Pages built from this table carry a caption listing the corrections that
affect them.
