#!/usr/bin/env python3
"""
Example usage of the 1212.mn API query module
"""

from query_api import API1212, MetadataStore, query_data
import json


def example_1_search_housing_prices():
    """Example: Search for housing price data"""
    print("=" * 60)
    print("Example 1: Housing Prices in Sukhbaatar District")
    print("=" * 60)

    result = query_data("apartment price Sukhbaatar", detailed=False)

    print(f"\nQuery: {result['query']}")
    print(f"Found {len(result['matched_tables'])} table(s)\n")

    for i, table in enumerate(result['matched_tables'][:3], 1):
        print(f"{i}. {table['name']}")
        print(f"   ID: {table['id']}")
        print(f"   Description: {table['description']}")
        print(f"   Unit: {table['unit']}")
        print(f"   Frequency: {table['frequency']}")
        print()


def example_2_list_sectors():
    """Example: List all available sectors"""
    print("=" * 60)
    print("Example 2: List All Sectors")
    print("=" * 60)

    api = API1212()
    sectors = api.get_sectors()

    if sectors:
        print(f"\nFound {len(sectors)} sectors:\n")
        for sector in sectors[:10]:  # Show first 10
            print(f"  - {sector.get('NAME_EN', sector.get('name_en', 'N/A'))}")
        print(f"\n  ... and {len(sectors) - 10} more")
    else:
        print("\nCould not fetch sectors from API")


def example_3_search_employment():
    """Example: Search for employment statistics"""
    print("=" * 60)
    print("Example 3: Employment Statistics")
    print("=" * 60)

    result = query_data("unemployment rate Ulaanbaatar", detailed=False)

    print(f"\nQuery: {result['query']}")

    if result['matched_tables']:
        print(f"Found {len(result['matched_tables'])} table(s)\n")
        table = result['matched_tables'][0]
        print(f"Top result: {table['name']}")
        print(f"Description: {table['description']}")
    else:
        print("No tables found")
        if 'message' in result:
            print(f"Note: {result['message']}")


def example_4_programmatic_access():
    """Example: Programmatic access to API"""
    print("=" * 60)
    print("Example 4: Programmatic API Access")
    print("=" * 60)

    api = API1212()
    store = MetadataStore()

    # Search metadata
    print("\nSearching for GDP tables...")
    tables = store.search_tables("GDP gross domestic product", limit=3)

    print(f"Found {len(tables)} table(s):\n")
    for table in tables:
        print(f"  [{table['id']}] {table['name_en']}")

    if tables:
        # Get detailed info for first table
        table_id = tables[0]['id']
        print(f"\nFetching details for: {table_id}")

        table_info = api.get_table_info(table_id)
        if table_info:
            print(f"Table structure: {json.dumps(table_info, indent=2)[:300]}...")
        else:
            print("Could not fetch table details from API")


def example_5_json_output():
    """Example: Get results as JSON"""
    print("=" * 60)
    print("Example 5: JSON Output")
    print("=" * 60)

    result = query_data("population demographics", detailed=False)

    print("\nJSON output:")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
    print("\n... (truncated)")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  1212.mn API Query Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    examples = [
        ("Housing Prices", example_1_search_housing_prices),
        ("List Sectors", example_2_list_sectors),
        ("Employment Stats", example_3_search_employment),
        ("Programmatic Access", example_4_programmatic_access),
        ("JSON Output", example_5_json_output),
    ]

    for name, func in examples:
        try:
            func()
            print("\n")
        except Exception as e:
            print(f"Error in {name}: {e}")
            print()

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nNote: Some examples require metadata to be initialized.")
    print("Run: python3 query_api.py --refresh")


if __name__ == '__main__':
    main()
