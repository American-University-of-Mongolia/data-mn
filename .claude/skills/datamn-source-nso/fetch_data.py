#!/usr/bin/env python3
"""
Fetch datasets from 1212.mn API using direct HTTP requests.

Supports bilingual output: fetches data in both English and Mongolian
and saves separate CSV files for each language.

Uses direct API calls to https://data.1212.mn/api/v1/
"""

import requests
import pandas as pd
from pathlib import Path
import sqlite3
import argparse
import json
from urllib.parse import quote
from typing import Optional, Dict, List, Any

# API Configuration
BASE_URL = "https://data.1212.mn/api/v1"

# Paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "metadata" / "tables.db"

# Supported languages
LANGUAGES = ['en', 'mn']
LANGUAGE_NAMES = {
    'en': 'English',
    'mn': 'Mongolian'
}


class NSO_API:
    """Direct API client for 1212.mn (no external packages required)"""

    def __init__(self, language: str = 'en'):
        self.language = language
        self.base_path = f"{BASE_URL}/{language}/NSO"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; datamn-fetch/1.0)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def get_table_metadata(self, sector_id: str, subsector_id: str, table_id: str) -> Optional[Dict]:
        """Get table metadata including variables and their values"""
        url = f"{self.base_path}/{quote(sector_id)}/{quote(subsector_id)}/{quote(table_id)}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching metadata: {e}")
            return None

    def fetch_data(self, sector_id: str, subsector_id: str, table_id: str,
                   query: Dict = None) -> Optional[Dict]:
        """
        Fetch actual data from the table.

        If query is None, fetches ALL data (all values from all variables).
        Returns json-stat2 format response.
        """
        url = f"{self.base_path}/{quote(sector_id)}/{quote(subsector_id)}/{quote(table_id)}"

        # If no query provided, first get metadata to build a query for all data
        if query is None:
            metadata = self.get_table_metadata(sector_id, subsector_id, table_id)
            if not metadata:
                return None
            query = self._build_all_data_query(metadata)

        try:
            response = self.session.post(url, json=query, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def _build_all_data_query(self, metadata: Dict) -> Dict:
        """Build a query that selects all values from all variables"""
        query = {
            "query": [],
            "response": {"format": "json-stat2"}
        }

        variables = metadata.get('variables', [])
        for var in variables:
            code = var.get('code', '')
            values = var.get('values', [])

            if code and values:
                query["query"].append({
                    "code": code,
                    "selection": {
                        "filter": "item",
                        "values": values
                    }
                })

        return query


def get_table_path(table_id: str) -> tuple:
    """Get sector and subsector for a table from metadata DB"""
    if not DB_PATH.exists():
        print(f"Warning: Metadata database not found at {DB_PATH}")
        print("Run: python3 query_api.py --refresh")
        return (None, None)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT sector_id, subsector_id
        FROM tables
        WHERE id = ?
    """, (table_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)


def jsonstat2_to_dataframe(data: Dict) -> pd.DataFrame:
    """
    Convert json-stat2 format to pandas DataFrame.

    json-stat2 structure:
    - dimension: dict of dimensions with their categories
    - value: flat array of values
    - size: array of dimension sizes
    - id: array of dimension IDs in order

    Column names are taken from each dimension's 'label' field (language-appropriate).
    """
    if not data:
        return pd.DataFrame()

    # Get dimensions and their labels
    dimensions = data.get('dimension', {})
    dim_ids = data.get('id', [])
    sizes = data.get('size', [])
    values = data.get('value', [])

    if not dim_ids or not values:
        return pd.DataFrame()

    # Build index arrays for each dimension
    # Also build column name mapping (dim_id -> human readable label)
    dim_value_labels = {}  # Maps dim_id to list of value labels
    dim_col_names = {}     # Maps dim_id to column name (from dimension's label field)

    for dim_id in dim_ids:
        dim = dimensions.get(dim_id, {})
        category = dim.get('category', {})
        index = category.get('index', {})
        labels = category.get('label', {})

        # Get the human-readable column name from dimension's label field
        # Falls back to dim_id if not available
        dim_col_names[dim_id] = dim.get('label', dim_id)

        # Create ordered list of value labels
        if isinstance(index, dict):
            # index is {code: position}
            ordered_codes = sorted(index.keys(), key=lambda x: index[x])
        else:
            # index is a list
            ordered_codes = index if index else list(labels.keys())

        dim_value_labels[dim_id] = [labels.get(code, code) for code in ordered_codes]

    # Build rows by iterating through all combinations
    rows = []

    # Calculate strides for index calculation
    strides = []
    stride = 1
    for s in reversed(sizes):
        strides.insert(0, stride)
        stride *= s

    for i, value in enumerate(values):
        row = {}
        temp = i
        for j, dim_id in enumerate(dim_ids):
            idx = temp // strides[j]
            temp = temp % strides[j]

            # Use the human-readable column name
            col_name = dim_col_names[dim_id]
            labels_list = dim_value_labels.get(dim_id, [])
            if idx < len(labels_list):
                row[col_name] = labels_list[idx]
            else:
                row[col_name] = f"Unknown_{idx}"

        row['value'] = value
        rows.append(row)

    return pd.DataFrame(rows)


def fetch_table(table_id: str, output_dir: Path, languages: List[str] = None) -> Dict[str, bool]:
    """
    Fetch a table in specified languages and save as CSV.

    Args:
        table_id: The NSO table ID (e.g., 'DT_NSO_0500_001V1.px')
        output_dir: Directory to save CSV files
        languages: List of languages ['en', 'mn'] or None for both

    Returns:
        Dict mapping language to success boolean
    """
    if languages is None:
        languages = LANGUAGES

    results = {}

    # Get sector and subsector from metadata
    sector_id, subsector_id = get_table_path(table_id)

    if not sector_id or not subsector_id:
        print(f"  Error: Table {table_id} not found in metadata database")
        print(f"  Try running: python3 query_api.py --refresh")
        return {lang: False for lang in languages}

    print(f"  Sector: {sector_id}")
    print(f"  Subsector: {subsector_id}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch in each language
    for lang in languages:
        print(f"\n  Fetching in {LANGUAGE_NAMES[lang]}...")

        api = NSO_API(language=lang)

        # Fetch data
        data = api.fetch_data(sector_id, subsector_id, table_id)

        if not data:
            print(f"    Failed to fetch data")
            results[lang] = False
            continue

        # Convert to DataFrame
        df = jsonstat2_to_dataframe(data)

        if df.empty:
            print(f"    No data returned (empty)")
            results[lang] = False
            continue

        # Generate output filename from table_id
        # DT_NSO_0500_001V1.px -> nso-0500-001v1
        name_part = table_id.replace('DT_NSO_', 'nso-').replace('.px', '').replace('_', '-').lower()
        output_file = output_dir / f"{name_part}-{lang}.csv"

        # Save CSV
        df.to_csv(output_file, index=False)

        print(f"    Saved: {output_file}")
        print(f"    Rows: {len(df)}, Columns: {list(df.columns)}")

        results[lang] = True

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Fetch NSO 1212.mn datasets in English and/or Mongolian',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch a specific table in both languages
  python3 fetch_data.py --table DT_NSO_0500_001V1.px --output ./output

  # Fetch only English
  python3 fetch_data.py --table DT_NSO_0500_001V1.px --lang en --output ./output

  # Fetch only Mongolian
  python3 fetch_data.py --table DT_NSO_0500_001V1.px --lang mn --output ./output
        """
    )
    parser.add_argument(
        '--table', '-t',
        required=True,
        help='Table ID to fetch (e.g., DT_NSO_0500_001V1.px)'
    )
    parser.add_argument(
        '--lang', '-l',
        choices=['en', 'mn', 'both'],
        default='both',
        help='Language to fetch: en, mn, or both (default: both)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('.'),
        help='Output directory (default: current directory)'
    )

    args = parser.parse_args()

    # Determine languages
    if args.lang == 'both':
        languages = LANGUAGES
    else:
        languages = [args.lang]

    print(f"Fetching table: {args.table}")
    print(f"Languages: {', '.join(LANGUAGE_NAMES[l] for l in languages)}")
    print(f"Output: {args.output.absolute()}")
    print("=" * 50)

    results = fetch_table(args.table, args.output, languages)

    print("\n" + "=" * 50)
    print("Results:")
    for lang, success in results.items():
        status = "Success" if success else "Failed"
        print(f"  {LANGUAGE_NAMES[lang]}: {status}")


if __name__ == '__main__':
    main()
