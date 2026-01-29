# Version 1 - Government Revenue and Expenditure

**Created**: 2026-01-29
**Source**: NSO 1212.mn
**Table ID**: DT_NSO_0800_001V1.px

## Raw Data Files

- `nso-0800-001v1-en.csv` - English version (315 rows: Revenue, Expenditure, Balance)
- `nso-0800-001v1-mn.csv` - Mongolian version (315 rows: Орлого, Зарлага, Тэнцэл)

## Processing Applied

1. Filtered to keep only Revenue and Expenditure (removed Balance)
2. Chart data: filtered to years >= 1991 (post-Soviet era)
3. Download data: includes all years (1921-2025)
4. Created bilingual CSVs with translated column headers
5. Created wide-format XLSX for Excel users

## Output

### Chart Files (1991-2025)
- 70 rows (35 Revenue + 35 Expenditure)
- `government-revenue-expenditure-en.csv`
- `government-revenue-expenditure-mn.csv`

### Download Files (1921-2025)
- 210 rows (105 Revenue + 105 Expenditure)
- `government-revenue-expenditure-all-en.csv`
- `government-revenue-expenditure-all-mn.csv`
- `government-revenue-expenditure.xlsx` (wide format)

## Data Range

- **Full Data**: 1921-2025 (105 years)
- **Chart Display**: 1991-2025 (35 years)

## Notes

- Raw data had leading whitespace in "Expenditure" column name
- Fixed by applying `.str.strip()` before filtering
- Values in million MNT (nominal, not inflation-adjusted)
