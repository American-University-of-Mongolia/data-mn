---
name: 1212mn-api
description: Query Mongolia's National Statistical Office (1212.mn) API v1 to retrieve statistical data about Mongolia including demographics, economy, housing prices, employment, and more
dependencies:
  - python3
  - python3-requests
  - sqlite3
---

# 1212.mn API Query Skill

This skill enables querying Mongolia's National Statistical Office (NSO) API v1 at data.1212.mn. It provides access to comprehensive statistical data about Mongolia.

## Setup

Before using this skill for the first time, you MUST refresh the metadata cache:

```bash
cd skills/1212mn-api
python3 query_api.py --refresh
```

This will download and cache all available tables and their metadata into a local SQLite database. This process may take 1-2 minutes as it fetches all sectors, subsectors, and tables.

## Usage

### Basic Query

When the user asks a question about Mongolia statistics, use this skill to search for relevant data:

1. **Parse the user's question** to identify key terms (e.g., "apartment price", "Sukhbaatar district", "employment rate")

2. **Run the query script**:
   ```bash
   python3 query_api.py [search terms]
   ```

3. **Interpret the results**:
   - The script returns matched tables with their descriptions, sectors, and metadata
   - Explain what data is available
   - If the exact data isn't available, suggest alternative datasets

### Examples

**Example 1: Housing Prices**
```
User: "What is the average apartment price in Sukhbaatar district?"

Action:
cd skills/1212mn-api && python3 query_api.py apartment price district

Response Pattern:
- Identify matching tables (e.g., tables with "орон сууц" (apartment) and "үнэ" (price))
- Note what the table actually contains (e.g., price per square meter by district)
- Explain: "The data shows average price per square meter, not total apartment price"
- Show the relevant table information
- Suggest related datasets if applicable
```

**Example 2: Employment Data**
```
User: "What's the unemployment rate in Ulaanbaatar?"

Action:
cd skills/1212mn-api && python3 query_api.py unemployment rate Ulaanbaatar

Response Pattern:
- Find employment/unemployment tables
- Check geographic granularity
- Provide available table info with time period
```

**Example 3: Population Statistics**
```
User: "How many people live in Mongolia?"

Action:
cd skills/1212mn-api && python3 query_api.py population Mongolia

Response Pattern:
- Find population tables
- Show tables with population counts by region, year, etc.
```

## Commands

### Search for data
```bash
python3 query_api.py [search terms]
```
Searches the metadata for tables matching the query terms.

### Get detailed data (with variable structure)
```bash
python3 query_api.py --detailed [search terms]
```
Fetches the actual table structure from the API showing available variables and their values.

### List all sectors
```bash
python3 query_api.py --sectors
```
Shows all 8 main sectors (Education/health, Regional development, Society/development, etc.)

### List all available tables
```bash
python3 query_api.py --list
```
Shows all tables in the database with their IDs, sectors, and descriptions (shows first 50 by default).

### Filter tables by sector
```bash
python3 query_api.py --list --sector "Population, household"
```
Shows only tables within a specific sector.

### Get JSON output
```bash
python3 query_api.py --json [search terms]
```
Returns results in JSON format for programmatic processing.

### Refresh metadata
```bash
python3 query_api.py --refresh
```
Updates the local metadata cache from the API. Use this periodically or when requested by the user.

### Use Mongolian language
```bash
python3 query_api.py --lang mn [search terms]
```
Query using Mongolian language API (returns Mongolian names and descriptions).

## Important Guidelines

### 1. Data Interpretation

- **Table names are in Mongolian**: Most table names use Cyrillic Mongolian script
- **Always explain what's available**: Tables contain specific variables and classifications
- **Check the variables**: Use `--detailed` to see what dimensions are available
- **Note the time period**: Tables have update timestamps showing freshness of data

### 2. Smart Query Matching

The system uses intelligent keyword matching with English-Mongolian synonyms:
- "apartment" matches "орон сууц" (housing)
- "price" matches "үнэ" (cost)
- "population" matches "хүн ам"
- "district" matches "дүүрэг"
- "employment" matches "ажил эрхлэлт", "хөдөлмөр"

### 3. Handling Missing Data

If the exact data requested isn't available:
1. Search for related tables
2. Explain what IS available
3. Suggest alternative queries
4. Offer to list all tables in the relevant sector

Example:
```
User asks: "Average apartment size in Sukhbaatar"
If not available: "The database doesn't have average apartment size, but it does have:
- Average price per square meter by district (DT_NSO_XXXX_XXX.px)
- Number of apartments by region and type
Would you like data from either of these tables?"
```

### 4. API Structure

The new API (v1) is hierarchical:
```
Sectors (8 main categories)
  └── Subsectors (thematic groupings)
      └── Tables (.px files with statistical data)
          └── Variables (dimensions like year, gender, age group)
```

**Example path:**
`Population, household` → `1_Population, household` → `DT_NSO_0300_001V2.px`

### 5. Understanding Table Structure

When you fetch detailed data, tables contain:
- **title**: Full table title in Mongolian
- **variables**: List of dimensions, each with:
  - **code**: Variable identifier
  - **text**: Variable name (e.g., "Хүйс" = Gender)
  - **values**: Coded values (e.g., ["0", "1", "2"])
  - **valueTexts**: Human-readable labels (e.g., ["All", "Male", "Female"])

### 6. Periodic Metadata Refresh

The metadata cache should be refreshed:
- When user explicitly requests it
- If queries consistently return no results
- Monthly for maintenance
- When NSO announces new datasets

To refresh:
```bash
cd skills/1212mn-api && python3 query_api.py --refresh
```

## Data Categories (Sectors)

The 1212.mn API includes 8 main sectors:

1. **Education, health** (Боловсрол, эрүүл мэнд)
2. **Regional development** (Бүсчилсэн хөгжил)
3. **Society, development** (Нийгэм, хөгжил)
4. **Historical data** (Түүхэн Статистик)
5. **Industry, service** (Үйлдвэрлэл, үйлчилгээ)
6. **Labour, business** (Хөдөлмөр, бизнес)
7. **Population, household** (Хүн ам, өрх)
8. **Economy, environment** (Эдийн засаг, байгаль орчин)

Each sector contains multiple subsectors with specific datasets.

## Error Handling

If the script returns errors:

1. **"Metadata not initialized"**: Run `python3 query_api.py --refresh`
2. **"No relevant tables found"**: Try different keywords, check Mongolian translations, or list all tables
3. **API connection errors**: Check internet connection, API might be temporarily unavailable
4. **Empty results**: The query might be too specific, try broader terms

## Output Format

The script outputs:
- **Query**: The search terms used
- **Matched Tables**: List of relevant tables with:
  - Table ID (e.g., DT_NSO_0300_001V2.px)
  - Name in Mongolian
  - Sector and subsector
  - Last update date
  - Full API path

With `--detailed`:
- **Title**: Full table title
- **Variables**: All available dimensions and their possible values

Use this information to provide a comprehensive answer to the user's question.

## Tips for Effective Use

1. **Understand Mongolian names**: Common terms:
   - Хүн ам = Population
   - Орон сууц = Apartment/Housing
   - Үнэ = Price
   - Дүүрэг = District
   - Аймаг = Province
   - Дундаж = Average
   - Нийслэл = Capital

2. **Use multiple keywords**: Combine location, subject, and metric
3. **Check the variables**: Use `--detailed` to understand table structure
4. **Consider geographic levels**: Data may be by country, province (аймаг), district (дүүрэг), or sub-district (сум, баг, хороо)
5. **Look for related data**: Often multiple tables provide complementary information

## Refreshing Data

When the user asks to update or refresh the data:

```bash
cd skills/1212mn-api && python3 query_api.py --refresh
```

This will:
1. Connect to the 1212.mn API v1
2. Fetch all current sectors (8 categories)
3. Fetch all subsectors within each sector
4. Download all table metadata
5. Update the local SQLite database
6. Rebuild the full-text search index

Inform the user when the refresh is complete and how many tables were updated.

## API Details

**Base URL**: `https://data.1212.mn/api/v1/{lang}/NSO/`

**Endpoints**:
- `GET /{lang}/NSO/` - List sectors
- `GET /{lang}/NSO/{sector}/` - List subsectors
- `GET /{lang}/NSO/{sector}/{subsector}/` - List tables
- `GET /{lang}/NSO/{sector}/{subsector}/{table}.px` - Get table data

**Languages**: `en` (English), `mn` (Mongolian)

**Response Format**:
- Lists: `[{"id": "...", "type": "...", "text": "..."}]`
- Tables: Also include `"updated": "2025-09-16T17:08:44"`
- Data: `{"title": "...", "variables": [...]}`
