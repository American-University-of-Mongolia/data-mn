#!/usr/bin/env python3
"""
Simple exploration of livestock data - try direct API access
"""

import requests
import json

# Try direct API access
SECTOR = "Industry, service"
SUBSECTOR = "Livestock"
TABLE_ID = "DT_NSO_1001_021V1.px"

def explore_direct():
    """Use direct API access"""
    base_url = "https://data.1212.mn/api/v1/en/NSO"

    # List subsectors
    print("Fetching subsectors for Industry, service...")
    url = f"{base_url}/{SECTOR}/"
    response = requests.get(url)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        subsectors = response.json()
        print(f"Found {len(subsectors)} subsectors")
        for sub in subsectors:
            print(f"  - {sub['id']}: {sub['text']}")

    # List tables in Livestock
    print(f"\nFetching tables in {SUBSECTOR}...")
    url = f"{base_url}/{SECTOR}/{SUBSECTOR}/"
    response = requests.get(url)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        tables = response.json()
        print(f"Found {len(tables)} tables")
        for table in tables:
            print(f"  - {table['id']}: {table['text']}")
            if 'updated' in table:
                print(f"    Updated: {table['updated']}")

    # Get table metadata
    print(f"\nFetching table metadata for {TABLE_ID}...")
    url = f"{base_url}/{SECTOR}/{SUBSECTOR}/{TABLE_ID}"
    response = requests.get(url)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        metadata = response.json()
        print(f"\nTable: {metadata.get('title', 'N/A')}")

        if 'variables' in metadata:
            print(f"Variables: {len(metadata['variables'])}")
            for var in metadata['variables']:
                print(f"\n  Variable: {var['code']}")
                print(f"  Text: {var['text']}")

                values = var.get('values', [])
                value_texts = var.get('valueTexts', [])

                print(f"  Number of values: {len(values)}")

                if len(values) > 0 and len(values) <= 30:
                    print("  All values:")
                    for i, (val, text) in enumerate(zip(values, value_texts)):
                        print(f"    {val}: {text}")
                elif len(values) > 30:
                    print("  First 20 values:")
                    for i, (val, text) in enumerate(zip(values[:20], value_texts[:20])):
                        print(f"    {val}: {text}")
                    print(f"    ... and {len(values) - 20} more")

        # Save metadata
        with open('/tmp/livestock_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print("\n\nMetadata saved to /tmp/livestock_metadata.json")

if __name__ == "__main__":
    explore_direct()
