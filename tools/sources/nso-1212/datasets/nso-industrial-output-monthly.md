# Mongolia Gross Industrial Output by Subdivision, Monthly

## Source Table
- **Table ID**: `DT_NSO_1100_001V2.px`
- **Sector**: Industry, service
- **Subsector**: Industry
- **Parent**: This IS the parent dataset

## API Path
```
GET /api/v1/{lang}/NSO/Industry%2C%20service/Industry/DT_NSO_1100_001V2.px
```

## Dimensions
1. **Subdivision** (Дэд салбар): 37 values (see full list below)
2. **Month** (Сар): 2017-09 to 2026-03 (monthly, YYYY-MM format)

## Time Range
- **Start**: 2017-09
- **End**: 2026-03 (latest as of fetch)
- **Frequency**: Monthly

## Subdivisions (English)
- Total
- Mining and quarrying
  - Mining of coal and lignite
  - Mining of metal ores
  - Extraction of crude petroleum and natural gas
  - Other mining and quarrying
  - Mining support service activities
- Manufacturing
  - Manufacture of food products
    - Processing and preserving of meat
    - Processing and preserving of fruit and vegetables
    - Manufacture of dairy products
    - Manufacture of grain mill products, starches and starch products
    - Manufacture of other food products
  - Manufacture of beverages
  - Manufacture of tobacco products
  - Manufacture of textiles
  - Manufacture of wearing apparel
  - Manufacture of leather and related products
  - Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials
  - Manufacture of paper and paper products
  - Printing and reproduction of recorded media
  - Manufacture of coke and refined petroleum products
  - Manufacture of chemicals and chemical products
  - Manufacture of pharmaceuticals, medicinal chemical and botanical products
  - Manufacture of rubber and plastics products
  - Manufacture of other non-metallic mineral products
  - Manufacture of basic metals
  - Manufacture of fabricated metal products, except machinery and equipment
  - Manufacture of other transport equipment
  - Manufacture of furniture
  - Other manufacturing
- Electricity, gas, steam and air conditioning supply
- Water supply; sewerage, waste management and remediation activities
  - Water collection, treatment and supply
  - Waste collection, treatment and disposal activities; materials recovery
  - Remediation activities and other waste management services

## Data Format (CSV columns)
- EN: `subdivision`, `date` (YYYY-MM), `value`
- MN: `дэд_салбар`, `огноо` (YYYY-MM), `утга`

## Values
- Unit: Million MNT (сая төгрөг)
- Gross industrial output (Аж үйлдвэрийн нийт бүтээгдэхүүн)

## Row Count
- Total rows: 3,914 (37 subdivisions x ~106 months)

## Suggested Child Datasets

### 1. industrial-output-total (single area chart)
- **Filter**: subdivision = "Total"
- **Chart**: Single-series area chart (monthly trend)
- **Title**: Mongolia Total Industrial Output, Monthly

### 2. industrial-output-by-sector (multi-line chart)
- **Filter**: Top-level sectors: Total, Mining and quarrying, Manufacturing, Electricity gas steam and air conditioning supply, Water supply sewerage waste management
- **Chart**: Multi-line chart
- **Title**: Mongolia Industrial Output by Major Sector, Monthly

### 3. industrial-output-mining (area chart)
- **Filter**: Mining subdivisions: Mining of coal and lignite, Mining of metal ores, Extraction of crude petroleum and natural gas, Other mining and quarrying
- **Chart**: Multi-line or grouped bar
- **Title**: Mongolia Mining Output by Type, Monthly

### 4. industrial-output-latest-bar (horizontal bar)
- **Filter**: Top-level subdivisions, latest month only
- **Chart**: Horizontal bar chart (ranking)
- **Title**: Mongolia Industrial Output by Subdivision, Latest Month
