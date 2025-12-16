# Dataset: Balance of Payments - Current Account

## Identification

- **ID**: `bop-current-account`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [balance-of-payments, current-account, trade, economy, mongolia, bop]

## Source Reference

- **Parent Dataset**: `nso-bop-monthly`
- **Parent Table ID**: `DT_NSO_0100_001V10.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Balance of Payments`
- **API Path**: `/en/NSO/Economy, environment/Balance of Payments/DT_NSO_0100_001V10.px`

## Title

- **EN**: Mongolia Current Account Balance, Million USD (2009-2025)
- **MN**: Монгол Улсын урсгал дансны тэнцэл, сая ам.доллар (2009-2025)

## Description

Mongolia's monthly current account balance showing surpluses and deficits from international trade and income flows. The current account tracks the flow of goods, services, primary income (investment returns, wages), and secondary income (transfers and remittances) between Mongolia and the rest of the world. A positive balance indicates a surplus (more inflows than outflows), while a negative balance indicates a deficit.

Data follows the IMF Balance of Payments Manual 6th Edition (BPM6) standards and spans from January 2009 to present.

## Variables

### Indicator (Үзүүлэлт)
This is a split dataset filtering for:
- `I. CURRENT ACCOUNT` / `I. УРСГАЛ ДАНС`: Total current account balance

The current account equals the sum of:
1. **Goods and services**: Trade balance (exports minus imports)
2. **Primary income**: Investment income, wages earned abroad
3. **Secondary income**: Transfers including remittances from Mongolians working abroad

### Month (Сар)
Monthly data from 2009-01 to 2025-09 (201 months)

### Value Unit
- Million USD
- Positive values = surplus (inflows > outflows)
- Negative values = deficit (outflows > inflows)

## Update Instructions

### Check for Updates

This is a split dataset. Updates are managed through the parent dataset `nso-bop-monthly`:

1. Check if parent dataset has updates:
   ```bash
   cd /home/ritz/Insync/robert@aum.edu.mn/Google Drive/data/tools
   python -m registry info nso-bop-monthly
   ```

2. If parent dataset `source_updated_at` is newer than this dataset's `updated_at`, trigger update

### Fetch Data

**This dataset does NOT fetch data directly.** It is derived from the parent dataset.

#### Update Process

1. Load parent data from `tools/versions/nso-bop-monthly/v{N}/data-en.csv`
2. Apply split filter:
   ```python
   import pandas as pd

   # Load parent data
   df = pd.read_csv("tools/versions/nso-bop-monthly/v{N}/data-en.csv")

   # Apply filter for current account only
   df_current = df[df['indicator'] == 'I. CURRENT ACCOUNT'].copy()

   # Clean column names
   df_current.columns = [c.lower().replace(' ', '_') for c in df_current.columns]

   # Strip whitespace from string columns (CRITICAL for chart matching)
   for col in df_current.select_dtypes(include=['object']).columns:
       df_current[col] = df_current[col].astype(str).str.strip()

   # Sort by date
   df_current = df_current.sort_values('month')

   # Save to version directory
   df_current.to_csv("tools/versions/bop-current-account/v{N}/data-en.csv", index=False)
   ```

3. Repeat for Mongolian version (`data-mn.csv`)

### Validation

- Values can be positive (surplus) or negative (deficit)
- Month format should be YYYY-MM
- Verify values match parent dataset for `I. CURRENT ACCOUNT` indicator
- No missing months in the time series

## Chart Configuration

### Chart Type
Area chart with line overlay

### Chart Specifications

**X-axis:**
- Field: `month`
- Type: `temporal`
- Format: YYYY-MM
- Title: "Month" / "Сар"

**Y-axis:**
- Field: `value`
- Type: `quantitative`
- Format: `,.0f` (comma-separated, no decimals)
- Title: "Balance (Million USD)" / "Тэнцэл (Сая ам.доллар)"

**Visual Encoding:**
- Mark: Area chart with gradient fill
- Line color: `#4c78a8` (primary brand color)
- Gradient: Top-down fade from `rgba(76, 120, 168, 0.3)` to `rgba(76, 120, 168, 0.01)`
- Interpolation: `monotone` (smooth curves)

**Hover Layer:**
- Required layered structure for nearest-point hover
- Point marks with `nearest: true` selection
- Tooltip displays: month (YYYY-MM format) and value (formatted with comma separators)

**Brand Compliance:**
- `config.axis.labelFontSize`: 14
- `config.axis.titleFontSize`: 16
- `config.axis.labelColor`: `#64748b`
- `config.axis.titleColor`: `#334155`
- No hardcoded width/height
- Must include `"format": {"type": "csv"}` in data specification

## Content Generation

### Excerpt Templates

**EN**: "Mongolia's current account balance was {latest_value}M USD in {latest_month}, {trend_direction} from {comparison_value}M USD in {comparison_month}. The current account {surplus_or_deficit} reflects the net flow of goods, services, income, and transfers between Mongolia and the rest of the world."

**MN**: "{latest_month} сард Монгол Улсын урсгал дансны тэнцэл {latest_value} сая ам.доллар байсан нь {comparison_month}-ийн {comparison_value} сая ам.доллартай харьцуулахад {trend_direction}. Урсгал дансны {surplus_or_deficit} нь Монгол Улс болон бусад орнуудын хооронд бараа, үйлчилгээ, орлого, шилжүүлгийн цэвэр урсгалыг харуулж байна."

### Key Findings

Auto-extract and include:
1. **Latest month value**: Current balance and date
2. **Trend direction**: Improving (more positive) or deteriorating (more negative)
3. **Year-to-date aggregate**: Sum of all months in current year
4. **12-month moving average**: Smoothed trend
5. **Surplus vs deficit periods**: Count of months with positive vs negative balance
6. **Largest surplus/deficit**: Peak values and dates in the dataset

### Tags
- `mongolia`
- `balance-of-payments`
- `current-account`
- `trade`
- `economy`
- `bop`
- `nso`
- `monthly`

### Keywords (SEO)
- "Mongolia current account"
- "Mongolia trade balance"
- "Mongolia BOP"
- "Mongolia balance of payments"
- "Mongolia current account deficit"
- "Mongolia current account surplus"
- "Mongolia international trade"

## Splits

This dataset IS a split. It has no further child splits.

## Notes

- **Data source**: Derived from parent dataset `nso-bop-monthly`
- **Split filter**: `indicator == "I. CURRENT ACCOUNT"`
- **IMF BPM6 standard**: Follows international methodology
- **Interpretation**:
  - **Surplus (positive)**: Mongolia receives more from the world than it sends out
  - **Deficit (negative)**: Mongolia sends more to the world than it receives
- **Typical drivers**:
  - Mining exports (positive contributor)
  - Machinery and equipment imports (negative contributor)
  - Remittances from abroad (positive contributor)
  - Investment income paid to foreign investors (negative contributor)
- **Economic significance**:
  - Large deficits can indicate reliance on foreign financing
  - Large surpluses indicate net savings
  - Persistent deficits may pressure the exchange rate
- **Seasonality**: Expect fluctuations due to seasonal commodity exports and import cycles
- **COVID-19 impact**: Notable changes in 2020 due to pandemic disruptions
- **File naming**:
  - Chart CSV: `bop-current-account-en.csv`, `bop-current-account-mn.csv`
  - Download CSV: `bop-current-account-all-en.csv`, `bop-current-account-all-mn.csv`
  - XLSX: `bop-current-account.xlsx`
  - Charts: `bop-current-account-en.json`, `bop-current-account-mn.json`

## Related Datasets

- `bop-trade-balance`: Goods exports vs imports (component of current account)
- `bop-services-balance`: Services trade (component of current account)
- `bop-remittances`: Personal transfers from abroad (component of secondary income)
- `bop-fdi-net`: Foreign direct investment flows
- `nso-bop-monthly`: Parent dataset with all BOP indicators
