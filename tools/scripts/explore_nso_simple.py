#!/usr/bin/env python3
"""
Simple exploration of NSO API
"""

import requests
import json

BASE_URL = "https://data.1212.mn/api/v1"

def get_sectors():
    """Get all sectors"""
    url = f"{BASE_URL}/en/NSO/"
    response = requests.get(url)
    return response.json()

def get_subsectors(sector_id):
    """Get subsectors for a sector"""
    url = f"{BASE_URL}/en/NSO/{sector_id}/"
    response = requests.get(url)
    return response.json()

def get_tables(sector_id, subsector_id):
    """Get tables in a subsector"""
    url = f"{BASE_URL}/en/NSO/{sector_id}/{subsector_id}/"
    response = requests.get(url)
    return response.json()

def main():
    print("=" * 60)
    print("NSO SECTORS")
    print("=" * 60)

    sectors = get_sectors()
    print(f"Type: {type(sectors)}")

    if isinstance(sectors, list):
        for i, sector in enumerate(sectors, 1):
            print(f"\n{i}. {sector}")
    else:
        print(json.dumps(sectors, indent=2))

    # Try to find economy sector
    print("\n" + "=" * 60)
    print("SEARCHING FOR ECONOMY/ENVIRONMENT SECTOR")
    print("=" * 60)

    economy_sectors = [s for s in sectors if isinstance(s, dict) and
                       ('economy' in str(s.get('text', '')).lower() or
                        'эдийн засаг' in str(s.get('text', '')))]

    if economy_sectors:
        sector = economy_sectors[0]
        print(f"Found: {sector}")

        print(f"\nGetting subsectors for: {sector.get('id')}")
        subsectors = get_subsectors(sector.get('id'))

        print("\nSubsectors:")
        for i, sub in enumerate(subsectors, 1):
            print(f"{i}. {sub}")

            # Look for CPI/price subsector
            if isinstance(sub, dict) and ('price' in str(sub.get('text', '')).lower() or
                                         'үнэ' in str(sub.get('text', ''))):
                print(f"\n  >>> Found CPI subsector!")
                print(f"  Getting tables...")

                tables = get_tables(sector.get('id'), sub.get('id'))
                print(f"\n  Tables ({len(tables)}):")

                for j, table in enumerate(tables[:20], 1):  # First 20 tables
                    print(f"  {j}. {table}")

                    # Look for inflation tables
                    if isinstance(table, dict):
                        table_text = str(table.get('text', '')).lower()
                        table_id = str(table.get('id', ''))

                        if 'inflation' in table_text or 'инфляц' in table_text or 'DT_NSO_0600_013' in table_id:
                            print(f"      ^^^ INFLATION TABLE FOUND! ^^^")

if __name__ == "__main__":
    main()
