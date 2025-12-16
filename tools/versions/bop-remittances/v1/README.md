# Version 1 - Initial Backup

## Metadata

- **Created**: 2025-12-16
- **Data Coverage**: 2009-01 to 2025-09
- **Source**: NSO 1212.mn Balance of Payments table `DT_NSO_0100_001V10.px`
- **Parent Dataset**: `nso-bop-monthly`
- **Filter**: `{"indicator": "of which: Personal transfers"}`

## Files Backed Up

| File | Description |
|------|-------------|
| `data-en.csv` | English version - 201 rows (monthly data) |
| `data-mn.csv` | Mongolian version - 201 rows (monthly data) |
| `data.xlsx` | Excel format with wide layout |
| `chart-en.json` | Vega-Lite chart specification (English) |
| `chart-mn.json` | Vega-Lite chart specification (Mongolian) |
| `page-en.mdx` | English MDX page |
| `page-mn.mdx` | Mongolian MDX page |

## Data Structure

- **Columns**: month, value
- **Time Range**: January 2009 - September 2025
- **Unit**: Million USD
- **Total Observations**: 201 months

## Statistics

**Sample Data Points:**
- Latest value (2025-09): Extracted from parent dataset
- Time series shows personal remittances sent to Mongolia from Mongolians working abroad
- Data follows IMF BPM6 standards

## Source Information

This is a split dataset extracted from the parent `nso-bop-monthly` dataset. The parent dataset contains full Balance of Payments data with 70 indicators. This split focuses on one specific indicator: "of which: Personal transfers" which represents personal remittances.

## Notes

- This version was created during initial definition file setup
- All existing production files have been backed up to this directory
- Dataset is already published with canonical slug `bop-remittances`
- First published: 2025-12-09
