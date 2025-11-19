---
name: 1212mn-api
description: Query Mongolia's National Statistical Office (1212.mn) open data API to retrieve statistical data about Mongolia including demographics, economy, housing prices, employment, and more
dependencies:
  - python3
  - python3-requests
  - sqlite3
---

# 1212.mn API Query Skill

This skill enables querying Mongolia's National Statistical Office (NSO) open data API at opendata.1212.mn. It provides access to comprehensive statistical data about Mongolia.

## Setup

Before using this skill for the first time, you MUST refresh the metadata cache:

```bash
cd skills/1212mn-api
python3 query_api.py --refresh
```

This will download and cache all available tables and their metadata into a local SQLite database.

## Usage

### Basic Query

When the user asks a question about Mongolia statistics, use this skill to search for relevant data:

1. **Parse the user's question** to identify key terms (e.g., "apartment price", "Sukhbaatar district", "employment rate")

2. **Run the query script**:
   ```bash
   python3 query_api.py [search terms]
   ```

3. **Interpret the results**:
   - The script returns matched tables with their descriptions, units, and metadata
   - Explain what data is available
   - If the exact data isn't available, suggest alternative datasets

### Examples

**Example 1: Housing Prices**
```
User: "What is the average apartment price in Sukhbaatar district?"

Action:
cd skills/1212mn-api && python3 query_api.py apartment price Sukhbaatar

Response Pattern:
- Identify matching tables (e.g., "Average price per square meter of apartments by district")
- Note the unit (e.g., MNT per square meter, not total price)
- Explain: "The data shows average price per square meter, not total apartment price"
- Show the relevant data if available
- Suggest related datasets if applicable (e.g., "Also available: apartment sales volume by district")
```

**Example 2: Employment Data**
```
User: "What's the unemployment rate in Ulaanbaatar?"

Action:
cd skills/1212mn-api && python3 query_api.py unemployment rate Ulaanbaatar

Response Pattern:
- Find employment/unemployment tables
- Check geographic granularity
- Provide available data with time period and source
```

**Example 3: Economic Indicators**
```
User: "Show me GDP growth for the last 5 years"

Action:
cd skills/1212mn-api && python3 query_api.py GDP growth

Response Pattern:
- Find GDP tables
- Note the frequency (annual, quarterly)
- Explain time periods available
```

## Commands

### Search for data
```bash
python3 query_api.py [search terms]
```
Searches the metadata for tables matching the query terms.

### List all available tables
```bash
python3 query_api.py --list
```
Shows all tables in the database with their IDs and descriptions.

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

### Get detailed data (slower)
```bash
python3 query_api.py --detailed [search terms]
```
Fetches actual statistical data from the API, not just table metadata.

## Important Guidelines

### 1. Data Interpretation

- **Always explain the units**: Many tables use rates, percentages, or per-capita measures
- **Note the time period**: Statistical data has specific collection periods
- **Explain limitations**: If exact data isn't available, suggest what is available
- **Provide context**: Include relevant metadata (source, last update, frequency)

### 2. Smart Query Matching

The system uses intelligent keyword matching with synonyms:
- "apartment" matches "housing", "residential", "dwelling"
- "price" matches "cost", "value", "rate"
- "district" matches "region", "area"

Be aware of these synonyms when interpreting queries.

### 3. Handling Missing Data

If the exact data requested isn't available:
1. Search for related tables
2. Explain what IS available
3. Suggest alternative queries
4. Offer to list all tables in the relevant category

Example:
```
User asks: "Average apartment size in Sukhbaatar"
If not available: "The database doesn't have average apartment size, but it does have:
- Average price per square meter by district
- Number of apartments sold by district and size category
Would you like data from either of these tables?"
```

### 4. Geographic Entities

Common geographic entities in Mongolia data:
- **Ulaanbaatar**: Capital city (sometimes broken down by districts)
- **Districts** (within Ulaanbaatar): Sukhbaatar, Bayanzurkh, Chingeltei, etc.
- **Aimags**: Provinces (21 aimags)
- **National**: Country-level aggregates

### 5. Periodic Metadata Refresh

The metadata cache should be refreshed:
- When user explicitly requests it
- If queries consistently return no results
- Periodically (suggest monthly)

To refresh:
```bash
cd skills/1212mn-api && python3 query_api.py --refresh
```

## Data Categories

The 1212.mn API includes data across 34 sectors including:

- **Demographics**: Population, migration, vital statistics
- **Economy**: GDP, inflation, trade, investment
- **Employment**: Labor force, unemployment, wages
- **Housing**: Prices, construction, sales
- **Education**: Enrollment, schools, literacy
- **Health**: Hospitals, diseases, healthcare access
- **Agriculture**: Production, livestock, land use
- **Industry**: Manufacturing, mining, production
- **Energy**: Consumption, production, prices
- **Transportation**: Infrastructure, traffic, vehicles
- **Finance**: Banking, insurance, stock market
- **Social**: Poverty, inequality, social services
- And many more...

## Error Handling

If the script returns errors:

1. **"Metadata not initialized"**: Run `python3 query_api.py --refresh`
2. **"No relevant tables found"**: Try different keywords or list all tables
3. **API connection errors**: Check internet connection, API might be temporarily unavailable
4. **Empty results**: The query might be too specific, try broader terms

## Output Format

The script outputs:
- **Query**: The search terms used
- **Matched Tables**: List of relevant tables with:
  - Table ID
  - Name
  - Description
  - Unit of measurement
  - Update frequency
  - Last update date
- **Message**: Any additional notes or suggestions

Use this information to provide a comprehensive answer to the user's question.

## Tips for Effective Use

1. **Start broad**: Use general terms first, then narrow down
2. **Use multiple keywords**: Combine location, subject, and metric
3. **Check units carefully**: Many statistics are rates, percentages, or per-capita
4. **Consider time periods**: Data may be annual, quarterly, or monthly
5. **Look for related data**: Often multiple tables provide complementary information

## Refreshing Data

When the user asks to update or refresh the data:

```bash
cd skills/1212mn-api && python3 query_api.py --refresh
```

This will:
1. Connect to the 1212.mn API
2. Download all current table metadata
3. Update the local SQLite database
4. Rebuild the search index

Inform the user when the refresh is complete and how many tables were updated.
