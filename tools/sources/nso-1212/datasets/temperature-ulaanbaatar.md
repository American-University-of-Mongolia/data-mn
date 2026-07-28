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
