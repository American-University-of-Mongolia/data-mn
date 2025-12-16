#!/usr/bin/env python3
"""
Fetch and process average salary data from NSO 1212.mn
Table: DT_NSO_0400_021V1.px - Monthly Average Nominal Wages
"""

import requests
import json
import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data.mn" / "public" / "datasets"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# NSO API parameters
BASE_URL = "https://data.1212.mn/api/v1"
SECTOR = 'Labour, business'
SUBSECTOR = 'Wages'
FOLDER = 'MONTHLY AVERAGE NOMINAL WAGES, by region, aimags and the Capital, by gender'
TABLE_ID = 'DT_NSO_0400_021V1.px'

def get_table_metadata():
    """Get table metadata"""
    url = f"{BASE_URL}/en/NSO/{SECTOR}/{SUBSECTOR}/{FOLDER}/{TABLE_ID}"
    print(f"Fetching metadata from: {url}")
    response = requests.get(url, timeout=15)
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
    url = f"{BASE_URL}/en/NSO/{SECTOR}/{SUBSECTOR}/{FOLDER}/{TABLE_ID}"
    print(f"\nPosting query to: {url}")

    response = requests.post(url, json=query, timeout=30)

    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None

    return response.json()

def jsonstat_to_dataframe(jsonstat_data):
    """Convert JSON-stat2 format to pandas DataFrame"""
    dataset = jsonstat_data

    # Get dimension info
    dimensions = dataset.get('dimension', {})
    size = dataset.get('size', [])
    values = dataset.get('value', [])

    # Extract dimension names and labels, skipping eliminated dimensions
    dim_names = []
    dim_values = []
    dim_size_idx = 0

    for dim_id in dimensions.keys():
        dim_info = dimensions[dim_id]
        is_eliminated = dim_info.get('extension', {}).get('elimination', False)

        if not is_eliminated:
            dim_names.append(dim_info.get('label', dim_id))

            # Get category labels
            categories = dim_info.get('category', {})
            if 'label' in categories:
                labels = list(categories['label'].values())
            else:
                labels = list(categories.get('index', {}).keys())

            dim_values.append(labels)

    # Create DataFrame - dimensions vary from left to right (leftmost slowest)
    # For size [3, 28, 30]: gender x region x year
    rows = []
    idx = 0

    if len(size) == 3:
        for i in range(size[0]):  # Gender
            for j in range(size[1]):  # Region
                for k in range(size[2]):  # Year
                    row = {
                        dim_names[0]: dim_values[0][i],
                        dim_names[1]: dim_values[1][j],
                        dim_names[2]: dim_values[2][k],
                        'value': values[idx] if idx < len(values) and values[idx] is not None else None
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

    # Fetch data
    print("\n" + "="*60)
    print("Fetching data...")
    data = fetch_data(metadata)

    if not data:
        print("Failed to fetch data")
        return

    # Save raw JSON for inspection
    raw_path = DATA_DIR / "average-salary-raw.json"
    with open(raw_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved raw JSON to: {raw_path}")

    # Convert to DataFrame
    print("\nParsing data...")
    df = jsonstat_to_dataframe(data)

    if df is not None:
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print("\nFirst 20 rows:")
        print(df.head(20))

        # Clean column names
        df.columns = ['gender', 'region', 'year', 'average_salary']

        # Clean values
        df['gender'] = df['gender'].str.strip()
        df['region'] = df['region'].str.strip()
        df['year'] = df['year'].astype(int)

        # Remove rows with None/NaN values
        df = df.dropna(subset=['average_salary'])

        # Save full dataset
        full_path = DATA_DIR / "average-salary-full.csv"
        df.to_csv(full_path, index=False)
        print(f"\nSaved full dataset: {full_path} ({len(df)} rows)")

        # Create split: National average only (TOTAL gender, National average region)
        national_df = df[
            (df['gender'] == 'TOTAL') &
            (df['region'] == 'National average')
        ][['year', 'average_salary']].copy()

        national_df = national_df.sort_values('year')

        # Save CSV
        csv_path = DATA_DIR / "average-salary.csv"
        national_df.to_csv(csv_path, index=False)
        csv_size = csv_path.stat().st_size
        print(f"\nNational Average Salary:")
        print(f"  CSV: {csv_path.name} ({csv_size:,} bytes)")
        print(f"  Rows: {len(national_df)}")

        # Save XLSX
        xlsx_path = DATA_DIR / "average-salary.xlsx"
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            national_df.to_excel(writer, index=False, sheet_name='Data')
        xlsx_size = xlsx_path.stat().st_size
        print(f"  XLSX: {xlsx_path.name} ({xlsx_size:,} bytes)")

        # Print statistics
        print(f"\nDataset Statistics:")
        print(f"  Years: {national_df['year'].min()}-{national_df['year'].max()}")
        print(f"  Min salary: {national_df['average_salary'].min():,.0f} MNT")
        print(f"  Max salary: {national_df['average_salary'].max():,.0f} MNT")
        print(f"  Latest ({national_df['year'].max()}): {national_df.iloc[-1]['average_salary']:,.0f} MNT")

        print("\n✓ Done! Created dataset with CSV and XLSX formats.")
    else:
        print("\nCould not parse data to DataFrame")

if __name__ == "__main__":
    main()
