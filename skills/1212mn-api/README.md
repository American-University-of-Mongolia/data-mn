# 1212.mn API Query Skill

This skill provides access to Mongolia's National Statistical Office (NSO) open data API at [opendata.1212.mn](http://opendata.1212.mn).

## Features

- **Smart Search**: Natural language queries with synonym matching
- **Metadata Caching**: Local SQLite database for fast table lookups
- **Full-Text Search**: FTS5-powered search across all table descriptions
- **Comprehensive Coverage**: Access to 34+ sectors of Mongolia statistical data

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Metadata Cache

```bash
python3 query_api.py --refresh
```

This downloads all available tables from the API and builds a local search index.

### 3. Query Data

```bash
# Search for tables
python3 query_api.py apartment price Sukhbaatar

# List all tables
python3 query_api.py --list

# Get JSON output
python3 query_api.py --json GDP growth

# Get detailed data (fetches from API)
python3 query_api.py --detailed unemployment rate
```

## Usage in Claude Code

This skill is automatically available in Claude Code. When you ask questions about Mongolia statistics, Claude will use this skill to find and retrieve relevant data.

**Example queries:**
- "What is the average apartment price in Sukhbaatar district?"
- "Show me unemployment statistics for Ulaanbaatar"
- "What's the GDP growth rate for Mongolia?"
- "How many people live in Ulaanbaatar?"

## Data Coverage

The 1212.mn API provides statistical data across multiple sectors:

### Demographics & Social
- Population statistics
- Migration data
- Vital statistics (births, deaths, marriages)
- Education enrollment and literacy
- Healthcare access and facilities
- Poverty and inequality measures

### Economy & Finance
- GDP and economic growth
- Inflation and price indices
- International trade
- Foreign investment
- Banking and financial services
- Stock market data

### Employment & Labor
- Labor force participation
- Unemployment rates
- Wages and salaries
- Employment by sector/industry
- Working conditions

### Housing & Real Estate
- **Apartment prices per square meter by district**
- Housing construction statistics
- Sales volume and transactions
- Residential building permits

### Industry & Production
- Manufacturing output
- Mining and minerals
- Energy production and consumption
- Agricultural production
- Livestock statistics

### Infrastructure & Services
- Transportation statistics
- Telecommunications
- Utilities and services
- Public infrastructure

## API Structure

The 1212.mn API is organized hierarchically:

```
Sectors (34 main categories)
  └── Subsectors
      └── Tables (specific datasets)
          └── Data (actual statistics with filters)
```

### API Endpoints

- `GET /api/Sector?type=en` - List all sectors
- `GET /api/Sector?subid={id}&type=en` - Get subsectors
- `GET /api/Itms?type=en` - List all tables
- `GET /api/Itms/{id}?type=en` - Get table details
- `POST /api/Data?type=en` - Query statistical data

## How It Works

### Metadata Caching

When you run `--refresh`, the tool:
1. Fetches all sectors from the API
2. Retrieves all available tables
3. Stores metadata in SQLite with full-text search index
4. Extracts and indexes keywords with synonyms

### Smart Search

The search engine:
- Matches your query against table names and descriptions
- Expands keywords using synonyms (e.g., "apartment" → "housing", "residential", "dwelling")
- Ranks results by relevance using BM25 algorithm
- Returns top matches with full metadata

### Query Execution

For detailed queries:
1. Search finds relevant tables
2. Tool fetches table structure and classifications
3. Constructs appropriate API query
4. Retrieves and formats the data

## File Structure

```
skills/1212mn-api/
├── SKILL.md              # Skill definition for Claude Code
├── query_api.py          # Main API query module
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore rules
└── metadata/
    └── tables.db        # SQLite metadata cache (generated)
```

## Maintaining the Metadata

The metadata cache should be refreshed periodically to ensure you have the latest tables:

```bash
python3 query_api.py --refresh
```

**When to refresh:**
- First time setup
- Monthly maintenance
- When queries consistently return no results
- After NSO announces new datasets

The refresh process takes 30-60 seconds depending on API response time.

## Example Outputs

### Search Query
```bash
$ python3 query_api.py apartment price district

Query: apartment price district
Found 3 relevant table(s)

1. Average price per square meter of newly built apartments by district
   ID: HOU_PRICE_NEW_01
   Description: Monthly average price per square meter for new construction
   Unit: MNT per square meter
   Frequency: Monthly
   Last Updated: 2025-10-01

2. Average price per square meter of old apartments by district
   ID: HOU_PRICE_OLD_01
   Description: Monthly average price per square meter for existing apartments
   Unit: MNT per square meter
   Frequency: Monthly
   Last Updated: 2025-10-01
```

### List Tables
```bash
$ python3 query_api.py --list | head -20

Available Tables (342):

  [DEMO_POP_01] Population by age group and gender
      Annual population statistics by age groups, gender, and region
      Unit: Persons, Frequency: Annual

  [ECON_GDP_01] Gross Domestic Product by sector
      Quarterly and annual GDP by economic sectors
      Unit: Million MNT, Frequency: Quarterly

  [EMP_RATE_01] Employment rate by region
      Labor force participation and employment rates
      Unit: Percentage, Frequency: Quarterly
```

## Technical Details

### Database Schema

**sectors table**: Top-level categories
- `id`: Sector ID
- `name_en`: English name
- `name_mn`: Mongolian name
- `description`: Sector description

**subsectors table**: Subcategories
- `id`: Subsector ID
- `sector_id`: Parent sector
- `name_en`, `name_mn`: Names in both languages

**tables table**: Individual datasets
- `id`: Table ID (used for API queries)
- `subsector_id`: Parent subsector
- `name_en`, `name_mn`: Table names
- `description`: Detailed description
- `keywords`: Extracted searchable keywords
- `unit`: Measurement unit
- `frequency`: Update frequency
- `last_updated`: Most recent data date
- `metadata`: Full JSON metadata from API

**tables_fts**: Full-text search virtual table
- FTS5 index for fast text search
- Indexes: id, name_en, description, keywords

### Keyword Extraction

The tool automatically extracts and expands keywords using synonym mapping:

**Synonyms:**
- apartment → housing, residential, dwelling, home
- price → cost, value, rate, tariff
- average → mean, typical
- district → region, area, zone
- income → earnings, salary, wage
- population → demographic, inhabitants, residents

This allows flexible querying - asking about "apartment cost" will match tables about "housing prices".

## Troubleshooting

### "Metadata not initialized"
Run `python3 query_api.py --refresh` to build the initial cache.

### "No relevant tables found"
- Try broader search terms
- Use `--list` to browse all available tables
- Check for typos in your query
- Consider the metadata might be outdated (refresh)

### API Connection Errors
- Check your internet connection
- Verify the API is accessible: `curl http://opendata.1212.mn/api/Sector?type=en`
- The API might be temporarily unavailable
- Some networks may block access to Mongolia domains

### Empty Data Results
Even with `--detailed` flag, some tables may return limited data based on:
- Your query parameters
- Data availability for specific time periods
- Geographic restrictions in the dataset

## Contributing

This skill is part of a collection of data tools. Contributions and improvements are welcome!

### Future Enhancements
- [ ] Add data visualization support
- [ ] Implement caching for frequently accessed data
- [ ] Support for Mongolian language queries
- [ ] Export results to CSV/Excel
- [ ] Time series analysis helpers
- [ ] Geographic data mapping

## License

This tool is provided as-is for querying publicly available statistical data from Mongolia's National Statistical Office.

## Links

- **API Documentation**: http://opendata.1212.mn/en/doc
- **NSO Website**: https://1212.mn
- **Data Downloads**: https://downloads.1212.mn

## Last Updated

This README reflects the skill structure as of November 2025. Run `--refresh` to get the most current available datasets.
