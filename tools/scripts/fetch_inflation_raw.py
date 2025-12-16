#!/usr/bin/env python3
"""
Fetch inflation data using raw API
"""

import requests
import json
import pandas as pd
from pathlib import Path

BASE_URL = "https://data.1212.mn/api/v1"
SECTOR = "Economy, environment"
SUBSECTOR = "Consumer Price Index"
TABLE_ID = "DT_NSO_0600_013V2.px"

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data.mn/public/datasets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_table_metadata():
    """Get table metadata"""
    url = f"{BASE_URL}/en/NSO/{SECTOR}/{SUBSECTOR}/{TABLE_ID}"
    print(f"Fetching metadata from: {url}")
    response = requests.get(url)
    return response.json()

def fetch_data(metadata):
    """Fetch the actual data"""
    # Build query from metadata
    query = {
        "query": [],
        "response": {"format": "json-stat2"}
    }

    for var in metadata['variables']:
        query['query'].append({
            "code": var['code'],
            "selection": {
                "filter": "item",
                "values": var['values']
            }
        })

    # Post query to get data
    url = f"{BASE_URL}/en/NSO/{SECTOR}/{SUBSECTOR}/{TABLE_ID}"
    print(f"\nPosting query to: {url}")
    print(f"Query: {json.dumps(query, indent=2, ensure_ascii=False)}")

    response = requests.post(url, json=query)

    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None

    return response.json()

def jsonstat_to_dataframe(jsonstat_data):
    """Convert JSON-stat2 format to pandas DataFrame"""
    # This is a simplified parser - full implementation would be more complex
    dataset = jsonstat_data

    # Get dimension info
    dimensions = dataset.get('dimension', {})
    size = dataset.get('size', [])
    values = dataset.get('value', [])

    # Extract dimension names and labels
    dim_names = []
    dim_values = []

    for dim_id, dim_size in zip(dimensions.keys(), size):
        dim_info = dimensions[dim_id]
        dim_names.append(dim_info.get('label', dim_id))

        # Get category labels
        categories = dim_info.get('category', {})
        if 'label' in categories:
            labels = list(categories['label'].values())
        else:
            labels = list(categories.get('index', {}).keys())

        dim_values.append(labels)

    # Create DataFrame
    # For 2D data (Indicator x Year)
    if len(dim_names) == 2:
        # Create rows for each combination
        rows = []
        idx = 0
        for i in range(len(dim_values[0])):
            for j in range(len(dim_values[1])):
                row = {
                    dim_names[0]: dim_values[0][i],
                    dim_names[1]: dim_values[1][j],
                    'value': values[idx] if idx < len(values) else None
                }
                rows.append(row)
                idx += 1

        df = pd.DataFrame(rows)
        return df

    return None

def main():
    # Get metadata
    print("Fetching table metadata...")
    metadata = get_table_metadata()

    print(f"\nTable: {metadata.get('title')}")
    print(f"\nVariables:")
    for var in metadata.get('variables', []):
        print(f"  {var['code']}: {var['text']}")
        print(f"    Values: {len(var.get('values', []))} items")
        print(f"    Sample: {var.get('values', [])[:10]}")
        print(f"    Value Texts: {var.get('valueTexts', [])[:10]}")

    # Fetch data
    print("\n" + "="*60)
    print("Fetching data...")
    data = fetch_data(metadata)

    if not data:
        print("Failed to fetch data")
        return

    # Try to parse the JSON-stat2 format
    print("\nParsing data...")
    print(f"Data keys: {data.keys()}")

    # Save raw JSON for inspection
    raw_path = OUTPUT_DIR / "inflation-rate-raw.json"
    with open(raw_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved raw JSON to: {raw_path}")

    # Try to convert to DataFrame
    df = jsonstat_to_dataframe(data)

    if df is not None:
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print("\nFirst 20 rows:")
        print(df.head(20))

        # Clean and save
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]

        # Save CSV
        csv_path = OUTPUT_DIR / "inflation-rate.csv"
        df.to_csv(csv_path, index=False)
        print(f"\nSaved CSV to: {csv_path}")

        # Save XLSX
        xlsx_path = OUTPUT_DIR / "inflation-rate.xlsx"
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        print(f"Saved XLSX to: {xlsx_path}")
    else:
        print("\nCould not parse data to DataFrame")

if __name__ == "__main__":
    main()
