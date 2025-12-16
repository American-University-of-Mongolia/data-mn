# Dataset: Personal Remittances

## Identification

- **ID**: `bop-remittances`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [remittances, bop, balance-of-payments, transfers, economy, mongolia]

## Source Reference

- **Parent Table ID**: `DT_NSO_0100_001V10.px`
- **Parent Dataset**: `nso-bop-monthly`
- **Sector**: `Economy, environment`
- **Subsector**: `Balance of Payments`
- **API Path**: `/en/NSO/Economy, environment/Balance of Payments/DT_NSO_0100_001V10.px`

## Title

- **EN**: Mongolia Personal Remittances (2009-2025)
- **MN**: Монгол Улсын хувийн гуйвуулга (2009-2025)

## Description

Personal remittances sent to Mongolia from Mongolians working abroad. This is a subset of the Balance of Payments data, extracted from the "Secondary income" component under the Current Account. Remittances represent an important source of foreign exchange for Mongolia and reflect the diaspora's economic contribution to the home country.

## Data Structure

This is a **split dataset** derived from the parent `nso-bop-monthly` dataset.

### Filter Criteria

```json
{
  "indicator": "of which: Personal transfers"
}
```

### Variables

- **Month (Сар)**: Monthly data from 2009-01 to 2025-09 (YYYY-MM format)
- **Value**: Remittance flows in million USD
  - Positive values indicate inflows to Mongolia
  - Negative values would indicate outflows (rare for this indicator)

### Data Characteristics

- **Unit**: Million USD
- **Frequency**: Monthly
- **Time Range**: January 2009 - September 2025 (201 months)
- **Seasonal Patterns**: May show patterns related to holiday seasons, mining sector employment cycles
- **Typical Range**: $10-50 million USD per month (varies by economic conditions)

## Update Instructions

### Parent Dataset Dependency

This dataset is automatically regenerated when the parent dataset `nso-bop-monthly` is updated. Do NOT fetch data independently for this split.

### Check for Updates

1. Query the parent table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/Balance of Payments/
   ```

2. Find `DT_NSO_0100_001V10.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry for `nso-bop-monthly`

4. If parent has updates, this split will be regenerated automatically

### Fetch Data (via parent)

```bash
# Fetch parent data
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0100_001V10.px --output ../../data/tools/versions/nso-bop-monthly/v1

# Filter to create split
cd ../../data/tools
python3 scripts/create_split.py \
  --parent nso-bop-monthly \
  --split bop-remittances \
  --filter '{"indicator": "of which: Personal transfers"}'
```

### Validation

- All values should be positive (remittances flow TO Mongolia)
- Month format should be YYYY-MM
- No missing months in the time series
- Values typically range from $10M to $50M USD per month
- Check for outliers that might indicate data errors

## Chart Configuration

### Chart Type
Single-series area chart (time series)

### Visual Specification

```json
{
  "mark": {
    "type": "area",
    "line": {"color": "#4c78a8", "strokeWidth": 2.5},
    "color": {
      "gradient": "linear",
      "stops": [
        {"offset": 0, "color": "rgba(76, 120, 168, 0.01)"},
        {"offset": 1, "color": "rgba(76, 120, 168, 0.3)"}
      ]
    },
    "interpolate": "monotone"
  },
  "encoding": {
    "x": {"field": "month", "type": "temporal", "title": "Month"},
    "y": {"field": "value", "type": "quantitative", "title": "Million USD"}
  }
}
```

### Brand Colors
- Primary: `#4c78a8` (blue) - for the single remittance line

## Content Generation

### Key Metrics to Calculate

- **Latest Month Value**: Most recent remittance amount
- **Year-to-Date (YTD)**: Total remittances so far this year
- **Year-over-Year Change**: Compare latest month to same month last year
- **12-Month Moving Average**: Smoothed trend
- **Annual Totals**: Sum by calendar year for historical comparison

### Excerpt Templates

**English**:
- "Mongolia received ${value}M USD in personal remittances in {month}, {trend} from the previous year."
- "Personal remittances totaled ${ytd}M USD in the first {months} of {year}, {comparison} the same period last year."

**Mongolian**:
- "{month} сард Монгол Улс {value} сая ам.долларын хувийн гуйвуулга хүлээн авсан."
- "{year} оны эхний {months} сард нийт {ytd} сая ам.долларын хувийн гуйвуулга ирсэн."

### Key Findings Suggestions

1. **Trend Analysis**: Is remittance flow increasing or decreasing over time?
2. **Economic Context**: How do remittances correlate with mining employment, Korean/Japanese labor demand?
3. **COVID-19 Impact**: Did pandemic affect remittance flows (border closures, employment)?
4. **Seasonal Patterns**: Are there consistent seasonal peaks (e.g., holidays, bonuses)?
5. **Economic Significance**: What % of GDP or current account do remittances represent?

### Common Tags
- mongolia
- remittances
- balance-of-payments
- bop
- transfers
- economy
- nso
- monthly

### Related Datasets

- `bop-current-account` - Overall current account balance
- `bop-monthly` - Parent dataset with full BOP structure
- `labour-force-abroad` - Mongolians working abroad (if available)
- `exchange-rate` - MNT/USD rate for local currency impact

## Notes

- **Definition**: "Personal transfers" in BPM6 terminology includes worker remittances and other person-to-person transfers
- **Source Countries**: Major sources include South Korea, Japan, and other countries with Mongolian labor migrants
- **Economic Impact**: Remittances provide important foreign exchange and support household consumption
- **Data Quality**: NSO follows IMF Balance of Payments Manual 6th Edition (BPM6) standards
- **Reporting Lag**: Typically 1-2 months delay between month-end and data publication
- **This is a split dataset**: Generated from parent `nso-bop-monthly`, not independently fetched

## Version History

### v1 (2025-12-09)
- Initial creation from parent dataset `nso-bop-monthly`
- Data range: 2009-01 to 2025-09
- 201 monthly observations
