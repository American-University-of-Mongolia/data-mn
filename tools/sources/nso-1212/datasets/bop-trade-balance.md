# Dataset: Trade Balance - Goods

## Identification

- **ID**: `bop-trade-balance`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [trade, exports, imports, trade-balance, goods, merchandise, bop, economy]

## Source Reference

- **Parent Dataset**: `nso-bop-monthly`
- **Parent Table ID**: `DT_NSO_0100_001V10.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Balance of Payments`
- **API Path**: `/en/NSO/Economy, environment/Balance of Payments/DT_NSO_0100_001V10.px`

## Title

- **EN**: Mongolia Trade Balance - Goods (2009-2025)
- **MN**: Монгол Улсын барааны худалдааны тэнцэл (2009-2025)

## Description

Mongolia's monthly exports, imports, and trade balance for merchandise goods. This dataset shows the value of physical goods exported and imported, allowing analysis of trade patterns, commodity cycles, and Mongolia's trade surplus or deficit over time. Data follows IMF BPM6 standards and is measured in million USD.

## Dataset Type

**Split Dataset** - This is a filtered view of the parent dataset `nso-bop-monthly`.

### Split Filter

```json
{
  "indicators": [
    "1.1 Export FOB (credit)",
    "1.2 Import FOB (debit)"
  ]
}
```

### Calculated Fields

- **Net Trade Balance**: Export FOB - Import FOB (calculated from the two indicators)

## Variables

### Indicator (Үзүүлэлт)
Three indicators/series:
- `Export`: Exports of goods (FOB - Free On Board basis)
- `Import`: Imports of goods (FOB basis)
- `Net`: Trade balance (Export - Import, calculated)

### Month (Сар)
Monthly data from 2009-01 to 2025-09 (201 months)

### Value
- **Unit**: Million USD
- **Range**: Exports and Imports are positive values; Net can be positive (surplus) or negative (deficit)

## Update Instructions

### Data Source

This dataset is automatically regenerated when the parent dataset `nso-bop-monthly` is updated.

### Transformation Steps

1. Load parent data from `tools/versions/nso-bop-monthly/v{N}/data.csv`
2. Filter to only these indicators:
   - `1.1 Export FOB (credit)`
   - `1.2 Import FOB (debit)`
3. Reshape from long to wide format:
   - Each row = one month
   - Columns: `month`, `export`, `import`
4. Calculate net trade balance:
   ```python
   df['net'] = df['export'] - df['import']
   ```
5. Reshape back to long format with three series:
   - Rows for Export
   - Rows for Import
   - Rows for Net
6. Export bilingual CSVs with translated indicator names

### Validation

- Export and Import values should be positive
- Net = Export - Import
- Month format should be YYYY-MM
- No missing months between 2009-01 and latest data
- All three series should have the same time coverage

## Chart Configuration

### Chart Type
Multi-line chart with three series

### Visual Encoding

- **X-axis**: month (temporal)
- **Y-axis**: value in million USD (quantitative)
- **Color Scale**:
  - Export: `#54a24b` (green - positive flow in)
  - Import: `#e45756` (red - outflow)
  - Net: `#4c78a8` (blue - overall balance)
- **Interpolation**: monotone (smooth curves)
- **Legend**: Top horizontal, showing all three series

### Tooltip

Display for each point:
- Month (YYYY-MM format)
- Indicator name (Export/Import/Net)
- Value (formatted as "###,###M USD")

## Key Findings Template

Auto-extract for MDX page:
- Latest month's export value
- Latest month's import value
- Latest month's net trade balance (surplus or deficit)
- Year-to-date trade balance vs previous year
- 12-month moving average of net balance
- Identify if current trend is improving or worsening

## Content Generation

### Excerpt Templates

**EN**: "In {month}, Mongolia exported ${export}M and imported ${import}M USD of goods, resulting in a {surplus/deficit} of ${net}M."

**MN**: "{month} сард Монгол Улс ${export} сая ам.долларын бараа экспортолж, ${import} сая ам.долларын бараа импортолсон нь ${net} сая ам.долларын {ашиг/алдагдал} үүсгэсэн."

### Common Tags
- mongolia
- trade
- exports
- imports
- trade-balance
- goods
- merchandise
- bop
- economy
- nso
- monthly

### Keywords (EN)
- Mongolia trade balance
- exports and imports
- merchandise trade
- trade surplus
- trade deficit
- goods trade
- FOB exports
- FOB imports

### Keywords (MN)
- Монгол худалдаа
- экспорт импорт
- барааны худалдаа
- худалдааны тэнцэл
- гадаад худалдаа

## Analysis Notes

### Key Patterns
- **Seasonality**: Q4 typically shows higher exports due to mining shipments
- **Commodity Dependency**: Heavily influenced by copper and coal prices
- **Trade Partners**: Major exports to China; imports from China, Russia, Japan

### Historical Context
- **2009-2011**: Mining boom period - growing exports
- **2012-2016**: Commodity price decline - trade balance worsened
- **2017-2019**: Recovery period
- **2020**: COVID-19 impact on trade volumes
- **2021-2024**: Post-pandemic recovery, high commodity prices

### Use Cases
- Monitor Mongolia's trade competitiveness
- Analyze commodity export cycles
- Track import dependency
- Assess economic vulnerability to external shocks
- Policy planning for trade diversification

## Notes

- Data follows IMF Balance of Payments Manual 6th Edition (BPM6) standards
- Values are in million USD (not billion)
- FOB (Free On Board) basis means goods valued at the border, excluding freight/insurance
- Export and Import values are gross flows, not net
- Positive Net = Trade surplus; Negative Net = Trade deficit
- **This is a split dataset** - raw data is stored in parent `nso-bop-monthly`
- Chart shows all three series (Export, Import, Net) on one chart for easy comparison
