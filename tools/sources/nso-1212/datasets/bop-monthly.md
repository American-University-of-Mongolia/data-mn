# Dataset: Balance of Payments (Monthly)

## Identification

- **ID**: `nso-bop-monthly`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [balance-of-payments, bop, current-account, trade, fdi, reserves, economy]

## Source Reference

- **Table ID**: `DT_NSO_0100_001V10.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Balance of Payments`
- **API Path**: `/en/NSO/Economy, environment/Balance of Payments/DT_NSO_0100_001V10.px`

## Title

- **EN**: Mongolia Balance of Payments (Monthly)
- **MN**: Монгол Улсын төлбөрийн тэнцэл (Сараар)

## Description

Monthly Balance of Payments data for Mongolia following IMF BPM6 standards. Includes Current Account (goods, services, income), Capital Account, Financial Account (FDI, portfolio, other investment), and Reserve Assets. Data spans from January 2009 to present.

## Variables

### Indicator (Үзүүлэлт)
70 indicators in hierarchical BOP structure:

**Current Account (I. УРСГАЛ ДАНС)**
- `I. CURRENT ACCOUNT`: Total current account balance
- `Goods and services`: Trade in goods and services
- `1. Goods`: Merchandise trade
- `1.1 Export FOB (credit)`: Exports of goods
- `1.2 Import FOB (debit)`: Imports of goods
- `2. Services`: Services trade
- `3. Primary income`: Wages, investment income
- `4. Secondary income`: Transfers (including remittances)
- `of which: Personal transfers`: Remittances from abroad

**Capital Account (II. ХӨРӨНГИЙН ДАНС)**
- `II. CAPITAL ACCOUNT`: Capital transfers

**Financial Account (III. САНХҮҮГИЙН ДАНС)**
- `III. FINANCIAL ACCOUNT`: Total financial flows
- `1. Direct investment`: Foreign Direct Investment
- `2. Portfolio investment`: Stocks, bonds
- `4. Other investment`: Loans, deposits

**Reserves (V. НӨӨЦ ХӨРӨНГӨ)**
- `V. RESERVE ASSETS`: Central bank reserves
- `1. Reserve`: Reserve assets
- `2. IMF loan`: IMF credit

### Month (Сар)
Monthly data from 2009-01 to 2025-09 (201 months)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/Balance of Payments/
   ```

2. Find `DT_NSO_0100_001V10.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0100_001V10.px --output ../../data/tools/versions/nso-bop-monthly
```

### Validation

- Values can be positive or negative (surplus/deficit)
- Values are in million USD
- Month format should be YYYY-MM
- Current account = Goods + Services + Primary income + Secondary income

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. bop-current-account

- **ID**: `bop-current-account`
- **Title EN**: Mongolia Current Account Balance (2009-2025)
- **Title MN**: Монгол Улсын урсгал дансны тэнцэл (2009-2025)
- **Filter**:
  - Indicator: `I. CURRENT ACCOUNT`
- **Chart Type**: area
- **Chart Config**:
  - X-axis: month
  - Y-axis: value (million USD)
  - Color: #4c78a8 (positive/surplus) - chart shows actual +/- values
- **Description EN**: Mongolia's monthly current account balance showing surpluses and deficits from international trade and income flows.
- **Description MN**: Монгол Улсын олон улсын худалдаа, орлогын урсгалаас үүссэн урсгал дансны сарын тэнцэл.
- **Key Findings**:
  - Current value and trend
  - Seasonal patterns
  - Annual aggregates

### 2. bop-trade-balance

- **ID**: `bop-trade-balance`
- **Title EN**: Mongolia Trade Balance - Goods (2009-2025)
- **Title MN**: Монгол Улсын барааны худалдааны тэнцэл (2009-2025)
- **Filter**:
  - Indicators: `1.1 Export FOB (credit)`, `1.2 Import FOB (debit)`, calculated Net
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: month
  - Y-axis: value (million USD)
  - Color: Export=#54a24b, Import=#e45756, Net=#4c78a8
- **Description EN**: Mongolia's monthly exports, imports, and trade balance for merchandise goods.
- **Description MN**: Монгол Улсын барааны экспорт, импорт, худалдааны цэвэр тэнцэл.
- **Key Findings**:
  - Export vs import volumes
  - Trade balance trend
  - Seasonal commodity patterns

### 3. bop-services-balance

- **ID**: `bop-services-balance`
- **Title EN**: Mongolia Services Trade Balance (2009-2025)
- **Title MN**: Монгол Улсын үйлчилгээний худалдааны тэнцэл (2009-2025)
- **Filter**:
  - Indicator: `2. Services`
- **Chart Type**: area
- **Chart Config**:
  - X-axis: month
  - Y-axis: value (million USD)
  - Color: #4c78a8
- **Description EN**: Mongolia's monthly services trade balance including transport, tourism, and other services.
- **Description MN**: Монгол Улсын тээвэр, аялал жуулчлал болон бусад үйлчилгээний худалдааны тэнцэл.
- **Key Findings**:
  - Tourism seasonality
  - Transport services trend
  - COVID-19 impact

### 4. bop-fdi-net

- **ID**: `bop-fdi-net`
- **Title EN**: Mongolia Foreign Direct Investment, Net (2009-2025)
- **Title MN**: Монгол Улсын шууд хөрөнгө оруулалт, цэвэр (2009-2025)
- **Filter**:
  - Indicator: `1. Direct investment`
- **Chart Type**: area
- **Chart Config**:
  - X-axis: month
  - Y-axis: value (million USD)
  - Color: #4c78a8
- **Description EN**: Net foreign direct investment flows into Mongolia, primarily driven by mining sector.
- **Description MN**: Монгол Улс руу орж буй шууд хөрөнгө оруулалтын цэвэр урсгал, голчлон уул уурхайн салбарт.
- **Key Findings**:
  - FDI trend by year
  - Mining investment cycles
  - Recent investment momentum

### 5. bop-reserve-assets

- **ID**: `bop-reserve-assets`
- **Title EN**: Mongolia Reserve Asset Changes (2009-2025)
- **Title MN**: Монгол Улсын нөөц хөрөнгийн өөрчлөлт (2009-2025)
- **Filter**:
  - Indicator: `V. RESERVE ASSETS`
- **Chart Type**: area
- **Chart Config**:
  - X-axis: month
  - Y-axis: value (million USD)
  - Color: #4c78a8
- **Description EN**: Monthly changes in Mongolia's official reserve assets held by the central bank.
- **Description MN**: Монгол банкны албан ёсны нөөц хөрөнгийн сарын өөрчлөлт.
- **Key Findings**:
  - Reserve accumulation/depletion
  - Crisis periods
  - Current reserve position

### 6. bop-remittances

- **ID**: `bop-remittances`
- **Title EN**: Mongolia Personal Remittances (2009-2025)
- **Title MN**: Монгол Улсын хувийн гуйвуулга (2009-2025)
- **Filter**:
  - Indicator: `of which: Personal transfers`
- **Chart Type**: area
- **Chart Config**:
  - X-axis: month
  - Y-axis: value (million USD)
  - Color: #4c78a8
- **Description EN**: Personal remittances sent to Mongolia from Mongolians working abroad.
- **Description MN**: Гадаадад ажиллаж буй Монгол иргэдээс ирсэн хувийн гуйвуулга.
- **Key Findings**:
  - Remittance trend
  - Source country patterns
  - Economic significance

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest month value
- Year-to-date aggregate
- Same period last year comparison
- 12-month moving average

### Common Tags
- mongolia
- balance-of-payments
- bop
- economy
- nso
- monthly

### Excerpt Templates

**bop-current-account**:
- EN: "Mongolia's current account balance was ${value}M USD in {month}, {trend} from the previous month."
- MN: "{month} сард Монгол Улсын урсгал дансны тэнцэл ${value} сая ам.доллар байв."

**bop-trade-balance**:
- EN: "Mongolia exported ${exports}M and imported ${imports}M USD of goods in {month}."
- MN: "{month} сард Монгол Улс ${exports} сая ам.долларын бараа экспортолж, ${imports} сая ам.долларын бараа импортолсон."

## Notes

- Data follows IMF Balance of Payments Manual 6th Edition (BPM6) standards
- Values are in million USD
- Positive values = surplus/credit, Negative values = deficit/debit
- Monthly data with strong seasonal patterns
- **Parent dataset**: This dataset (`nso-bop-monthly`) stores the raw data; only the splits are published to data.mn
