# Data.mn Vision & Strategy

## Mission

**Data.mn collects all publicly available data on Mongolia that is up-to-date and relevant for decision makers and the public today.**

We make this data easily accessible and searchable. In the future, we aim to add analysis on top of this data to aid leaders and stakeholders in decision-making.

## Target Audience

| Audience | Needs |
|----------|-------|
| **General Public** | Easy access to facts about Mongolia, simple visualizations |
| **Researchers** | Downloadable datasets, methodology documentation, historical data |
| **Government Organizations** | Current statistics, cross-sector comparisons, trend analysis |
| **International Organizations** | Standardized data, English translations, reliable sources |
| **Journalists** | Quick facts, embeddable charts, citation-ready data |
| **Businesses** | Market data, economic indicators, demographic trends |

## Core Principles

### 1. Data Quality Over Quantity

We prioritize accurate, well-documented data over breadth. Each dataset includes:
- Clear source attribution
- Methodology notes
- Update frequency
- Known limitations

### 2. Bilingual by Default

All content exists in both English and Mongolian:
- Separate CSV files for each language (`-en.csv`, `-mn.csv`)
- Parallel MDX pages (`/en/data/...`, `/mn/data/...`)
- Translated category names and metadata

### 3. User-Friendly Splits (Statista-Style)

Raw multi-dimensional data is transformed into focused, single-topic datasets:

```
Raw Source Data                    User-Friendly Splits
─────────────────                  ────────────────────
Population by Age, Sex, Year  →    Total Population
                              →    Population Pyramid (Latest Year)
                              →    Population by Sex
                              →    Working Age Population
```

Each split has one clear story to tell.

### 4. URLs Are Forever

Once published, URLs never break. See [URL Stability Principles](principles/url-stability.md).

- URLs are permanent commitments
- Renames create redirects
- Deprecation, never deletion

### 5. Declarative Over Imperative

Data collection is defined in markdown files, not hardcoded scripts:
- Source definitions describe *how* to access data
- Dataset definitions describe *what* to extract
- Agents interpret definitions and adapt when sources change

### 6. Transparency

Every dataset shows:
- Original source with link
- Last updated date
- Version history
- Any transformations applied

## Current Scope

### Data Sources (Active)

| Source | Type | Coverage |
|--------|------|----------|
| **NSO 1212.mn** | API | 1,135+ statistical tables covering population, economy, employment, housing, trade, etc. |
| **MRPAM** | PDF | Mining and petroleum statistics |
| **Bank of Mongolia** | Mixed | Financial and monetary statistics |

### Categories

- Demographics (Хүн ам зүй)
- Economy (Эдийн засаг)
- Employment (Хөдөлмөр эрхлэлт)
- Housing (Орон сууц)
- Mining (Уул уурхай)
- Finance (Санхүү)
- Agriculture (Хөдөө аж ахуй)
- Education (Боловсрол)
- Health (Эрүүл мэнд)
- Trade (Худалдаа)
- Energy (Эрчим хүч)
- Tourism (Аялал жуулчлал)

## Roadmap

### Phase 1: Foundation ✅
- Core website with bilingual support
- NSO data integration
- Registry and version tracking
- URL stability system

### Phase 2: Expansion (Current)
- Add more NSO datasets
- MRPAM PDF extraction
- Bank of Mongolia integration
- Automated update checking

### Phase 3: Analysis
- Trend analysis and insights
- Cross-dataset comparisons
- Economic indicators dashboard
- Automated report generation

### Phase 4: Community
- Data request system
- User feedback integration
- API access for developers
- Embeddable widgets

## Non-Goals

Things we intentionally do NOT do:

1. **Real-time data** - We focus on official statistics, not live feeds
2. **Raw data dumps** - We curate and contextualize, not just mirror
3. **Paywalled content** - All data remains freely accessible
4. **User-generated content** - We maintain editorial control
5. **Predictive models** - We present facts, not forecasts (for now)

## Success Metrics

How we measure progress:

- **Coverage**: Number of active datasets across categories
- **Freshness**: Percentage of datasets updated within expected frequency
- **Usage**: Page views, downloads, search queries
- **Quality**: Zero broken links, validated data, accurate translations
- **Trust**: Citations in research, media mentions, government adoption

## Technical Foundation

The system is built on:

- **Astro** - Static site generation for speed and reliability
- **SQLite** - Registry database for dataset tracking
- **Vega-Lite** - Interactive, responsive visualizations
- **Conda** - Reproducible Python environment (`datamn`)
- **Direct API calls** - No external package dependencies for data fetching

See `CLAUDE.md` files for implementation details.
