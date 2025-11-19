# 1212.mn API Query Skill

This skill provides access to Mongolia's National Statistical Office (NSO) API v1 at [data.1212.mn](https://data.1212.mn).

## Features

- **Smart Search**: Natural language queries with English-Mongolian synonym matching
- **Metadata Caching**: Local SQLite database for fast table lookups
- **Full-Text Search**: FTS5-powered search across all table names and descriptions
- **Comprehensive Coverage**: Access to 8 sectors with hundreds of statistical tables

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Metadata Cache

```bash
python3 query_api.py --refresh
```

This downloads all available tables from the API and builds a local search index. Takes 1-2 minutes.

### 3. Query Data

```bash
# Search for tables
python3 query_api.py apartment price district

# List all sectors
python3 query_api.py --sectors

# List all tables
python3 query_api.py --list

# Get detailed table structure
python3 query_api.py --detailed population

# Get JSON output
python3 query_api.py --json employment rate
```

## Usage in Claude Code

This skill is automatically available in Claude Code. When you ask questions about Mongolia statistics, Claude will use this skill to find and retrieve relevant data.

**Example queries:**
- "What is the average apartment price in Sukhbaatar district?"
- "Show me population statistics for Ulaanbaatar"
- "What's the unemployment rate?"
- "How many households are in Mongolia?"

## API Structure

The 1212.mn API v1 uses a hierarchical path-based structure:

```
https://data.1212.mn/api/v1/{lang}/NSO/
├── Sector 1 (e.g., "Population, household")
│   ├── Subsector 1 (e.g., "1_Population, household")
│   │   ├── Table 1 (e.g., "DT_NSO_0300_001V2.px")
│   │   └── Table 2
│   └── Subsector 2
└── Sector 2
```

### API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /{lang}/NSO/` | List all sectors | `/en/NSO/` |
| `GET /{lang}/NSO/{sector}/` | List subsectors | `/en/NSO/Population, household/` |
| `GET /{lang}/NSO/{sector}/{subsector}/` | List tables | `/en/NSO/Population, household/1_Population, household/` |
| `GET /{lang}/NSO/{sector}/{subsector}/{table}.px` | Get table data | `/en/NSO/Population, household/1_Population, household/DT_NSO_0300_001V2.px` |

**Languages:** `en` (English), `mn` (Mongolian)

## Data Coverage

The API includes 8 main sectors:

### 1. **Education, health** (Боловсрол, эрүүл мэнд)
Schools, hospitals, healthcare, literacy, enrollment

### 2. **Regional development** (Бүсчилсэн хөгжил)
Regional statistics, infrastructure, local development

### 3. **Society, development** (Нийгэм, хөгжил)
Social indicators, development metrics

### 4. **Historical data** (Түүхэн Статистик)
Historical time series and long-term trends

### 5. **Industry, service** (Үйлдвэрлэл, үйлчилгээ)
Manufacturing, mining, production, services

### 6. **Labour, business** (Хөдөлмөр, бизнес)
Employment, unemployment, wages, business statistics

### 7. **Population, household** (Хүн ам, өрх)
Population counts, demographics, households, migration

### 8. **Economy, environment** (Эдийн засаг, байгаль орчин)
GDP, trade, prices, inflation, environment

## How It Works

### Metadata Caching

When you run `--refresh`, the tool:
1. Fetches all 8 sectors from the API
2. Retrieves subsectors for each sector
3. Downloads all table metadata
4. Stores everything in SQLite with full-text search index
5. Extracts keywords with English-Mongolian synonym mappings

### Smart Search

The search engine:
- Matches your query against table names (Mongolian and English IDs)
- Expands keywords using synonyms:
  - "apartment" → "орон сууц", "housing", "residential", "dwelling"
  - "price" → "үнэ", "cost", "value", "rate"
  - "population" → "хүн ам", "inhabitants", "residents"
- Ranks results by relevance using BM25 algorithm
- Returns top matches with metadata

### Query Execution

For detailed queries:
1. Search finds relevant tables
2. Tool fetches table structure from API
3. Returns variable definitions with possible values
4. Shows what data dimensions are available

## Response Formats

### List Endpoints (Sectors, Subsectors, Tables)
```json
[
  {
    "id": "Population, household",
    "type": "1",
    "text": "Хүн ам, өрх"
  }
]
```

### Table Data Endpoint
```json
{
  "title": "ХҮН АМЫН ТОО, хүйс, насны бүлэг, жилээр",
  "variables": [
    {
      "code": "Хүйс",
      "text": "Хүйс",
      "values": ["0", "1", "2"],
      "valueTexts": ["Бүгд", "Эрэгтэй", "Эмэгтэй"]
    }
  ]
}
```

## File Structure

```
skills/1212mn-api/
├── SKILL.md              # Skill definition for Claude Code
├── query_api.py          # Main API query module
├── examples.py           # Example usage patterns
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore rules
└── metadata/
    └── tables.db        # SQLite metadata cache (generated)
```

## Common Mongolian Terms

When searching or interpreting results, these terms are common:

| Mongolian | English |
|-----------|---------|
| Хүн ам | Population |
| Өрх | Household |
| Орон сууц | Apartment/Housing |
| Үнэ | Price |
| Дундаж | Average |
| Дүүрэг | District |
| Аймаг | Province |
| Нийслэл | Capital |
| Он | Year |
| Хүйс | Gender |
| Насны бүлэг | Age group |
| Ажил эрхлэлт | Employment |
| Ажилгүйдэл | Unemployment |
| Орлого | Income |
| Боловсрол | Education |
| Эрүүл мэнд | Health |

## Maintaining the Metadata

Refresh the metadata cache periodically:

```bash
python3 query_api.py --refresh
```

**When to refresh:**
- First time setup (required)
- Monthly maintenance
- When queries return no results
- After NSO announces new datasets

The refresh process typically takes 1-2 minutes.

## Example Outputs

### Search Query
```bash
$ python3 query_api.py population gender age

Query: population gender age
Found 2 relevant table(s)

1. ХҮН АМЫН ТОО, хүйс, насны бүлэг, жилээр
   ID: DT_NSO_0300_003V1.px
   Sector: Population, household
   Subsector: 1_Population, household
   Last Updated: 2025-09-16T17:07:54
```

### Detailed Query
```bash
$ python3 query_api.py --detailed population

1. ХҮН АМЫН ТОО, хүйс, насны бүлэг, жилээр
   ...
   Variables:
      - Хүйс: 3 values
      - Насны бүлэг: 16 values
      - Он: 40 values
```

### List Sectors
```bash
$ python3 query_api.py --sectors

Available Sectors (8):

  [Education, health]
      EN: Education, health
      MN: Боловсрол, эрүүл мэнд

  [Population, household]
      EN: Population, household
      MN: Хүн ам, өрх
  ...
```

## Troubleshooting

### "Metadata not initialized"
Run `python3 query_api.py --refresh` to build the initial cache.

### "No relevant tables found"
- Try broader search terms
- Use both English and Mongolian keywords
- List all tables with `--list` to browse
- Check specific sector with `--list --sector "Population, household"`

### API Connection Errors
- Check your internet connection
- Verify API is accessible: `curl https://data.1212.mn/api/v1/en/NSO/`
- API might be temporarily unavailable
- Some networks may block Mongolia domains

### Empty or Unexpected Results
- Table names are in Mongolian - check the keyword mapping
- Use `--detailed` to see what variables/dimensions are available
- Consider the data might be organized differently than expected

## Advanced Usage

### Programmatic Access

```python
from query_api import API1212, MetadataStore, query_data

# Search for tables
result = query_data("apartment price", detailed=False)
for table in result['matched_tables']:
    print(table['name_mn'])

# Direct API access
api = API1212(language='en')
sectors = api.get_sectors()
tables = api.get_tables("Population, household", "1_Population, household")

# Metadata queries
store = MetadataStore()
matches = store.search_tables("employment rate", limit=5)
```

### Custom Queries

```bash
# Filter by specific sector
python3 query_api.py --list --sector "Economy, environment"

# Use Mongolian language API
python3 query_api.py --lang mn хүн ам

# Get JSON for processing
python3 query_api.py --json GDP | jq '.matched_tables[0].name_mn'
```

## Contributing

Improvements and suggestions are welcome! Areas for enhancement:

- [ ] Better Mongolian keyword extraction
- [ ] Data visualization support
- [ ] Export to CSV/Excel
- [ ] Time series helpers
- [ ] Geographic data integration
- [ ] Caching of frequently accessed tables

## Links

- **API Base**: https://data.1212.mn/api/v1/
- **NSO Website**: https://1212.mn
- **Old API Docs**: http://opendata.1212.mn/en/doc (deprecated)

## Version History

- **v2.0** (Nov 2025): Updated for new API v1 at data.1212.mn
- **v1.0** (Nov 2025): Initial release with old API

---

**Last Updated**: November 2025
