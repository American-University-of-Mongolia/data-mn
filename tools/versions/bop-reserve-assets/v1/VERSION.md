# Version 1 - bop-reserve-assets

## Version Information

- **Version**: 1
- **Created**: 2025-12-09
- **Data As Of**: 2025-09 (September 2025)
- **Parent Dataset**: nso-bop-monthly
- **Parent Table**: DT_NSO_0100_001V10.px

## Dataset Details

- **ID**: bop-reserve-assets
- **Title (EN)**: Mongolia Reserve Asset Changes (2009-2025)
- **Title (MN)**: Монгол Улсын нөөц хөрөнгийн өөрчлөлт (2009-2025)
- **Category**: Economy / Эдийн засаг
- **Source**: NSO 1212.mn (National Statistics Office)

## Data Characteristics

- **Time Period**: January 2009 to September 2025
- **Frequency**: Monthly
- **Total Records**: 201 months (202 rows including header)
- **Unit**: Million USD
- **Indicator**: V. RESERVE ASSETS (net change in official reserve assets)

## Split Configuration

This dataset is a filtered split from the parent `nso-bop-monthly` dataset.

**Filter Applied**:
```json
{
  "indicator": "V. RESERVE ASSETS"
}
```

## Files Included

- `bop-reserve-assets-en.csv` - English version (201 data rows)
- `bop-reserve-assets-mn.csv` - Mongolian version (201 data rows)
- `bop-reserve-assets.xlsx` - Excel format (wide layout)

## Data Sample

| Month | Value (Million USD) |
|-------|---------------------|
| 2009-01 | 4.038 |
| 2009-02 | -25.783 |
| 2009-03 | -3.863 |
| 2009-04 | 15.539 |
| ... | ... |
| 2025-09 | (latest value) |

## Data Interpretation

- **Positive values**: Increase in reserve assets (accumulation)
- **Negative values**: Decrease in reserve assets (depletion/use)
- Values represent net monthly changes, not stock levels
- Data follows IMF BPM6 (Balance of Payments Manual 6th Edition) standards

## Key Periods

- **2009-2015**: Post-crisis recovery, moderate fluctuations
- **2016**: Economic crisis period, significant reserve depletion
- **2017-2019**: Recovery phase, reserve accumulation
- **2020**: COVID-19 impact, volatility
- **2021-2025**: Commodity boom period, generally positive flows

## Update History

### v1 (2025-12-09)
- Initial version created from parent dataset nso-bop-monthly
- Data covers January 2009 to September 2025 (201 months)
- Generated bilingual CSV files and Excel export
- Created MDX pages for both English and Mongolian versions
- Published to data.mn with canonical URL

## Notes

- This dataset shows CHANGES (flows) in reserves, not total reserve levels (stock)
- For total reserve holdings, refer to Bank of Mongolia's official statistics
- Large swings indicate balance of payments pressures or central bank intervention
- Data is sourced from the NSO's official balance of payments statistics
- Split dataset automatically regenerates when parent dataset updates
