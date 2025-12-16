# Version 1 - gdp-sector-trends

## Version Information

- **Version**: 1
- **Created**: 2025-12-03
- **Data Period**: 1990 to 2024
- **Source**: NSO 1212.mn (parent dataset: nso-gdp-by-economic-activity)
- **Parent Version**: v1

## Files

- `data-en.csv` - English version (sector, year, value columns)
- `data-mn.csv` - Mongolian version (translated sector names)
- `data.xlsx` - Wide format Excel file for downloads

## Data Structure

### CSV Format (Long)
```
sector,year,value
Mining,1990,1599.30
Agriculture,1990,1597.14
Trade,1990,2090.51
...
```

### Excel Format (Wide)
```
year | Agriculture | Construction | Manufacturing | Mining | Trade | Transport
1990 | 1597.14     | 735.57       | 2607.99       | 1599.30| 2090.51| 1044.80
...
```

## Sectors

This dataset tracks the six major economic sectors of Mongolia:

1. **Mining and quarrying** - Mongolia's dominant sector (extractive industries)
2. **Agriculture, forestry, fishing and hunting** - Traditional sector (livestock, crops)
3. **Wholesale and retail trade; repair of motor vehicles and motorcycles** - Commerce
4. **Manufacturing** - Industrial production
5. **Construction** - Building and infrastructure
6. **Transportation and storage** - Logistics

## Data Source

This split dataset is derived from the parent dataset `nso-gdp-by-economic-activity` by:
1. Filtering indicator to: `GDP, at current prices`
2. Selecting the top 6 major economic sectors
3. Excluding minor sectors and the "Total" aggregate
4. Reshaping to focus on time trends across sectors

## Statistics

- **Rows**: 210 rows (35 years × 6 sectors)
- **Time Coverage**: 1990 - 2024 (35 years)
- **Value Unit**: Million MNT at current prices
- **Value Range**: 735.57M MNT (Construction 1990) to 21,980,612.94M MNT (Mining 2024)

### Key Data Points (2024)

| Sector | GDP (Million MNT) | Share of Top 6 |
|--------|-------------------|----------------|
| Mining | 21,980,612.94 | 46.7% |
| Trade | 8,793,230.75 | 18.7% |
| Manufacturing | 4,495,483.47 | 9.6% |
| Transport | 4,439,528.88 | 9.4% |
| Construction | 2,696,383.17 | 5.7% |
| Agriculture | 4,729,664.93 | 10.0% |

### Growth Since 1990

| Sector | 1990 Value | 2024 Value | Growth Multiple |
|--------|------------|------------|-----------------|
| Mining | 1,599.30 | 21,980,612.94 | 13,750x |
| Trade | 2,090.51 | 8,793,230.75 | 4,206x |
| Transport | 1,044.80 | 4,439,528.88 | 4,249x |
| Agriculture | 1,597.14 | 4,729,664.93 | 2,962x |
| Manufacturing | 2,607.99 | 4,495,483.47 | 1,724x |
| Construction | 735.57 | 2,696,383.17 | 3,666x |

## Historical Context

### 1990-1995: Economic Transition
- Mongolia transitioned from Soviet-planned economy to market economy
- All sectors started from very low base values
- High inflation distorts nominal growth comparisons

### 1995-2005: Stabilization and Mining Emergence
- Economy stabilized after turbulent transition period
- Mining sector began to overtake agriculture
- FDI started flowing into extractive industries

### 2005-2015: Mining Boom
- Oyu Tolgoi and Tavan Tolgoi development
- Mining became dominant economic sector
- Construction and trade sectors grew to support mining

### 2015-2019: Commodity Price Adjustment
- Global commodity prices fell
- Mining sector growth slowed
- Economic diversification efforts

### 2020-2024: Recovery and Continued Mining Dominance
- COVID-19 impact in 2020
- Strong recovery driven by coal and copper exports
- Mining sector represents nearly half of GDP among major sectors

## Update Notes

Initial version created from parent dataset nso-gdp-by-economic-activity v1.

The dataset clearly shows Mongolia's economic transformation from a traditional agriculture-based economy to a mining-dominated economy over the past 34 years.
