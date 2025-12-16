# Weekly Flour Prices by Region - Version 1

## Version Information

- **Version**: 1
- **Created**: 2025-12-16
- **Dataset ID**: `weekly-flour-prices-aimags`
- **Parent Dataset**: `nso-weekly-prices-aimags`
- **Source Table**: `DT_NSO_0300_010V5.px`

## Data Period

- **First Date**: 2024-01-02
- **Last Date**: 2025-12-01
- **Frequency**: Weekly
- **Total Weeks**: 97+

## Filter Applied

```json
{
  "Products": "Flour, grade 1, prepacked, kg"
}
```

## Files in This Version

This directory should contain version backups of:

1. **Raw data from parent** (if applicable):
   - Parent dataset's filtered data before transformation

2. **Processed data**:
   - `weekly-flour-prices-aimags-en.csv` - Chart data (4 regional aggregates)
   - `weekly-flour-prices-aimags-mn.csv` - Chart data (Mongolian)
   - `weekly-flour-prices-aimags-all-en.csv` - Full data (all 25 regions)
   - `weekly-flour-prices-aimags-all-mn.csv` - Full data (Mongolian)
   - `weekly-flour-prices-aimags.xlsx` - Wide format (all regions as columns)

3. **Metadata**:
   - Processing logs
   - Data quality notes
   - Any transformation scripts used

## Regions Included

### Regional Aggregates (4 - used in charts)
- Central region (Төвийн бүс)
- Eastern region (Зүүн бүс)
- Western region (Баруун бүс)
- Khangai region (Хангайн бүс)

### Individual Aimags (21 - available in downloads)
Arkhangai, Bayan-Ulgii, Bayankhongor, Bulgan, Darkhan-Uul, Dornod, Dornogovi, Dundgovi, Govi-Altai, Govisumber, Khentii, Khovd, Khuvsgul, Orkhon, Selenge, Sukhbaatar, Tuv, Umnugovi, Uvs, Uvurkhangai, Zavkhan

## Data Characteristics

### Value Range (December 2025)
- **Minimum**: ~1,000 MNT/kg
- **Maximum**: ~1,500 MNT/kg
- **Average**: ~1,200-1,400 MNT/kg

### Notes
- All prices are for grade 1, prepacked flour
- Weekly averages across reporting locations
- Regional aggregates calculated from constituent aimags
- Ulaanbaatar NOT included (separate dataset)

## Update Notes

This is a split dataset that updates automatically when parent dataset `nso-weekly-prices-aimags` is refreshed. When parent updates:

1. Filter is re-applied to extract flour data
2. CSV files regenerated (chart subset + full data)
3. XLSX file regenerated (wide format)
4. Chart JSON files remain unchanged (unless structure changes)
5. MDX pages remain unchanged (unless content update needed)

## Validation Checks

Before publishing each version:
- [ ] All price values are positive
- [ ] Date values are valid weekly dates
- [ ] No unrealistic price jumps (>50% week-over-week)
- [ ] Regional aggregates match constituent aimag data
- [ ] Bilingual CSV files have identical structure
- [ ] XLSX pivot format is correct (dates as rows, regions as columns)
