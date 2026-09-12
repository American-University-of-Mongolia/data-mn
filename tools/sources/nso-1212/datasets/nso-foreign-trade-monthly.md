# Dataset: Mongolia Foreign Trade Monthly

## Identification

- **ID**: `nso-foreign-trade-monthly`
- **Source**: `nso-1212`
- **Category**: Trade
- **Tags**: [mongolia, foreign-trade, exports, imports, monthly, trade-balance]

## Source Reference

- **Table ID**: `DT_NSO_1400_003V1.px`
- **Sector**: `Foreign Trade`
- **Subsector**: `Foreign trade`
- **API Path**: `/en/NSO/Foreign Trade/Foreign trade/DT_NSO_1400_003V1.px`

## Title

- **EN**: Mongolia Foreign Trade Monthly, Million USD (1997–2026)
- **MN**: Монгол Улсын гадаад худалдаа сараар, сая ам.дол (1997–2026)

## Description

Monthly foreign trade data for Mongolia from January 1997 to July 2026, covering total turnover, exports, imports, and trade balance in million USD, sourced from the National Statistics Office. Monthly data reveals strong seasonality in Mongolia's trade flows — exports spike during summer and autumn coal shipping seasons, while imports rise mid-year alongside construction material deliveries.

## Variables

### Indicator (Үзүүлэлт)
Four indicators/series:
- `Total turnover` / `Нийт эргэлт`: Total trade turnover
- `Exports` / `Экспорт`: Total exports (FOB value)
- `Imports` / `Импорт`: Total imports (FOB value)
- `Balance` / `Тэнцэл`: Trade balance (exports minus imports, may be negative)

### Month (Сар)
Monthly data from 1997-01 to 2026-07 (355 months), format `YYYY-MM`

### Value
- **Unit**: Million USD
- **Columns EN**: `indicator`, `month`, `value_usd_mn`
- **Columns MN**: `үзүүлэлт`, `сар`, `value_usd_mn`
- **Rows**: 1420 (355 months x 4 indicators)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Foreign Trade/Foreign trade/
   ```

2. Find `DT_NSO_1400_003V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1400_003V1.px --output ./output
```

### Data Transformation

1. **Keep all four indicators**:
   - Total turnover, Exports, Imports, Balance

2. **Clean column names**:
   - EN: `indicator`, `month`, `value_usd_mn`
   - MN: `үзүүлэлт`, `сар`, `value_usd_mn`
   - Strip whitespace from all string columns

3. **Data validation**:
   - Balance may be negative; turnover/exports/imports should be positive
   - Month values should be valid YYYY-MM strings

4. **Export files**:
   - Chart CSV: `nso-foreign-trade-monthly-en.csv` and `nso-foreign-trade-monthly-mn.csv`
   - Excel XLSX: `nso-foreign-trade-monthly.xlsx` (with English and Mongolian sheets)

### Validation

- All four indicators should have matching months (355 each)
- Total turnover should equal Exports + Imports per month
- Balance should equal Exports - Imports per month
- EN/MN row counts and totals must match

## Chart Configuration

### Chart Type
Multi-line chart with four series

### Visual Encoding

- **X-axis**: month (temporal)
- **Y-axis**: value in million USD (quantitative)
- **Color**: indicator (Total turnover, Exports, Imports, Balance)

### Tooltip

Display for each point:
- Month
- Indicator name
- Value (formatted as "$###,###M USD")

## Content Generation

### Key Findings Template

Auto-extract for MDX page:
- Latest month's turnover, export, import, and balance values
- Seasonal patterns (summer/autumn export spikes)
- Post-pandemic recovery trend

### Common Tags
- mongolia
- foreign-trade
- exports
- imports
- monthly
- trade-balance
- nso

### Keywords (EN)
- Mongolia foreign trade monthly
- Mongolia monthly exports
- Mongolia monthly imports
- Mongolia trade 2026

### Keywords (MN)
- Монгол гадаад худалдаа сарын
- Монгол сарын экспорт
- Монгол сарын импорт

### Excerpt Templates

**EN**: "Monthly foreign trade data for Mongolia from January 1997 to July 2026, covering total turnover, exports, imports, and trade balance in million USD, sourced from the National Statistics Office."

**MN**: "Монгол Улсын 1997 оны 1-р сараас 2026 оны 7-р сар хүртэлх гадаад худалдааны нийт эргэлт, экспорт, импорт, баланс сараар сая ам.доллараар."

## Notes

- Raw version backup at `tools/versions/nso-foreign-trade-monthly/v1/` uses the
  source table's original headers (`Main indicators of foreign trade,Month,value`);
  published CSVs use cleaned headers (`indicator,month,value_usd_mn`)
- Values are in million USD, FOB basis
- Updated monthly by NSO
