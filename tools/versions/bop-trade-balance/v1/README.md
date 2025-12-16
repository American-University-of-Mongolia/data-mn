# Version 1 - bop-trade-balance

## Version Information

- **Version**: 1
- **Created**: 2025-12-09
- **Data Period**: 2009-01 to 2025-09
- **Source**: NSO 1212.mn (parent dataset: nso-bop-monthly)
- **Parent Version**: v1

## Files

- `data-en.csv` - English version (month, indicator, value columns)
- `data-mn.csv` - Mongolian version (translated indicator names)
- `data.xlsx` - Wide format Excel file for downloads

## Data Structure

### CSV Format (Long)
```
month,indicator,value
2009-01,Export,192.7
2009-01,Import,177.7
2009-01,Net,15.0
```

### Excel Format (Wide)
```
month       | Export | Import | Net
2009-01     | 192.7  | 177.7  | 15.0
```

## Indicators

1. **Export**: Exports of goods (FOB - Free On Board) in million USD
2. **Import**: Imports of goods (FOB) in million USD
3. **Net**: Trade balance (Export - Import) in million USD

## Data Source

This split dataset is derived from the parent dataset `nso-bop-monthly` by:
1. Filtering to indicators: `1.1 Export FOB (credit)` and `1.2 Import FOB (debit)`
2. Calculating the net trade balance
3. Reshaping to long format with three series (Export, Import, Net)

## Statistics

- **Rows**: 603 rows (201 months × 3 indicators)
- **Time Coverage**: January 2009 - September 2025
- **Export Range**: 192.7M - 1,127.7M USD
- **Import Range**: 177.7M - 1,161.7M USD
- **Latest Trade Balance** (2025-09): +94.0M USD (surplus)

## Update Notes

Initial version created from parent dataset nso-bop-monthly v1.
