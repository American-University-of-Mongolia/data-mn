#!/usr/bin/env python3
"""
1212.mn API Query Module
Handles queries to Mongolia's National Statistical Office open data API
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# API Configuration
BASE_URL = "http://opendata.1212.mn/api"
DEFAULT_TYPE = "en"  # Language: 'en' for English, 'mn' for Mongolian

# Paths
SCRIPT_DIR = Path(__file__).parent
METADATA_DIR = SCRIPT_DIR / "metadata"
DB_PATH = METADATA_DIR / "tables.db"


class API1212:
    """Client for interacting with 1212.mn API"""

    def __init__(self, language: str = DEFAULT_TYPE):
        self.language = language
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; 1212mn-skill/1.0)',
            'Accept': 'application/json'
        })

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request to API"""
        if params is None:
            params = {}
        params['type'] = self.language

        url = f"{BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error querying API: {e}", file=sys.stderr)
            return None

    def _post(self, endpoint: str, data: Dict, params: Optional[Dict] = None) -> Any:
        """Make POST request to API"""
        if params is None:
            params = {}
        params['type'] = self.language

        url = f"{BASE_URL}/{endpoint}"
        try:
            response = self.session.post(url, json=data, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error querying API: {e}", file=sys.stderr)
            return None

    def get_sectors(self) -> Optional[List[Dict]]:
        """Get list of all sectors"""
        return self._get("Sector")

    def get_subsectors(self, sector_id: str) -> Optional[List[Dict]]:
        """Get list of subsectors for a sector"""
        return self._get("Sector", params={'subid': sector_id})

    def get_tables(self) -> Optional[List[Dict]]:
        """Get list of all tables"""
        return self._get("Itms")

    def get_table_info(self, table_id: str) -> Optional[Dict]:
        """Get detailed information about a table including classifications"""
        return self._get(f"Itms/{table_id}")

    def get_data(self, query: Dict) -> Optional[Any]:
        """
        Get statistical data

        Args:
            query: Query parameters as dict, typically includes:
                - TBL_ID: Table ID
                - PERIOD: Time period filter
                - CODE: Classification codes
        """
        return self._post("Data", data=query)

    def get_package_data(self, query: Dict) -> Optional[Any]:
        """Get package statistical data"""
        return self._post("Package", data=query)


class MetadataStore:
    """Manages local metadata cache in SQLite"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Create database and tables if they don't exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sectors (
                id TEXT PRIMARY KEY,
                name_en TEXT,
                name_mn TEXT,
                description TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subsectors (
                id TEXT PRIMARY KEY,
                sector_id TEXT,
                name_en TEXT,
                name_mn TEXT,
                description TEXT,
                updated_at TEXT,
                FOREIGN KEY (sector_id) REFERENCES sectors(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                id TEXT PRIMARY KEY,
                subsector_id TEXT,
                name_en TEXT,
                name_mn TEXT,
                description TEXT,
                keywords TEXT,
                unit TEXT,
                frequency TEXT,
                last_updated TEXT,
                metadata TEXT,
                updated_at TEXT,
                FOREIGN KEY (subsector_id) REFERENCES subsectors(id)
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS tables_fts USING fts5(
                id,
                name_en,
                description,
                keywords,
                content=tables,
                content_rowid=rowid
            )
        """)
        conn.commit()
        conn.close()

    def refresh_metadata(self, api: API1212):
        """Refresh all metadata from API"""
        print("Refreshing metadata from 1212.mn API...")
        conn = sqlite3.connect(self.db_path)
        now = datetime.now().isoformat()

        # Fetch and store sectors
        print("Fetching sectors...")
        sectors = api.get_sectors()
        if sectors:
            for sector in sectors:
                conn.execute("""
                    INSERT OR REPLACE INTO sectors (id, name_en, name_mn, description, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    sector.get('ID', sector.get('id', '')),
                    sector.get('NAME_EN', sector.get('name_en', '')),
                    sector.get('NAME_MN', sector.get('name_mn', '')),
                    sector.get('DESCRIPTION', sector.get('description', '')),
                    now
                ))
            conn.commit()
            print(f"  Stored {len(sectors)} sectors")

        # Fetch and store all tables
        print("Fetching tables...")
        tables = api.get_tables()
        if tables:
            for table in tables:
                table_id = table.get('TBL_ID', table.get('id', ''))

                # Extract keywords from name and description
                name = table.get('TBL_NM_EN', table.get('name_en', ''))
                desc = table.get('TBL_DESC_EN', table.get('description', ''))
                keywords = self._extract_keywords(name, desc)

                conn.execute("""
                    INSERT OR REPLACE INTO tables
                    (id, subsector_id, name_en, name_mn, description, keywords,
                     unit, frequency, last_updated, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    table_id,
                    table.get('SUBSECTOR_ID', ''),
                    name,
                    table.get('TBL_NM_MN', ''),
                    desc,
                    keywords,
                    table.get('UNIT', ''),
                    table.get('FREQUENCY', ''),
                    table.get('LAST_UPDATE', ''),
                    json.dumps(table),
                    now
                ))

            # Update FTS index
            conn.execute("INSERT INTO tables_fts(tables_fts) VALUES('rebuild')")
            conn.commit()
            print(f"  Stored {len(tables)} tables")

        conn.close()
        print(f"Metadata refresh completed at {now}")

    def _extract_keywords(self, name: str, description: str) -> str:
        """Extract searchable keywords from name and description"""
        # Combine and lowercase
        text = f"{name} {description}".lower()

        # Common synonyms and related terms
        synonyms = {
            'apartment': ['housing', 'residential', 'dwelling', 'home'],
            'price': ['cost', 'value', 'rate', 'tariff'],
            'average': ['mean', 'typical'],
            'district': ['region', 'area', 'zone'],
            'income': ['earnings', 'salary', 'wage'],
            'population': ['demographic', 'inhabitants', 'residents'],
            'gdp': ['gross domestic product', 'economy'],
            'employment': ['job', 'work', 'labor', 'occupation'],
        }

        # Extract keywords
        keywords = set()
        for word in text.split():
            if len(word) > 3:  # Only words longer than 3 chars
                keywords.add(word.strip('.,;:()[]{}'))

        # Add synonyms for matched keywords
        for key, values in synonyms.items():
            if key in text:
                keywords.update(values)
                keywords.add(key)
            for value in values:
                if value in text:
                    keywords.add(key)
                    keywords.update(values)

        return ' '.join(sorted(keywords))

    def search_tables(self, query: str, limit: int = 10) -> List[Dict]:
        """Search tables using full-text search"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Prepare search query
        search_terms = query.lower().split()
        fts_query = ' OR '.join(search_terms)

        cursor = conn.execute("""
            SELECT t.*,
                   bm25(tables_fts) as rank
            FROM tables t
            JOIN tables_fts ON tables_fts.id = t.id
            WHERE tables_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_table_by_id(self, table_id: str) -> Optional[Dict]:
        """Get table by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("SELECT * FROM tables WHERE id = ?", (table_id,))
        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def list_all_tables(self) -> List[Dict]:
        """List all tables in the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT id, name_en, description, unit, frequency, last_updated
            FROM tables
            ORDER BY name_en
        """)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results


def query_data(query_text: str, detailed: bool = False) -> Dict:
    """
    Main query function that searches for relevant tables and optionally fetches data

    Args:
        query_text: Natural language query
        detailed: If True, fetch actual data from API

    Returns:
        Dict with results including matched tables and optionally data
    """
    api = API1212()
    store = MetadataStore()

    # Check if metadata exists
    if not DB_PATH.exists() or os.path.getsize(DB_PATH) < 1024:
        print("Metadata not found. Please run with --refresh flag first.")
        return {
            'error': 'Metadata not initialized',
            'message': 'Run: python query_api.py --refresh'
        }

    # Search for relevant tables
    print(f"Searching for: {query_text}")
    tables = store.search_tables(query_text, limit=5)

    if not tables:
        return {
            'query': query_text,
            'matched_tables': [],
            'message': 'No relevant tables found. Try different keywords or check available tables with --list'
        }

    result = {
        'query': query_text,
        'matched_tables': []
    }

    # Format table results
    for table in tables:
        table_info = {
            'id': table['id'],
            'name': table['name_en'],
            'description': table['description'],
            'unit': table['unit'],
            'frequency': table['frequency'],
            'last_updated': table['last_updated']
        }

        # If detailed, fetch actual data
        if detailed:
            print(f"  Fetching data for: {table['name_en']}...")
            table_meta = api.get_table_info(table['id'])
            if table_meta:
                table_info['classifications'] = table_meta

            # You would construct appropriate query here based on the table structure
            # This is a placeholder - actual query construction needs table-specific logic
            data = api.get_data({'TBL_ID': table['id']})
            if data:
                table_info['data'] = data

        result['matched_tables'].append(table_info)

    return result


def main():
    """CLI interface for the API"""
    import argparse

    parser = argparse.ArgumentParser(description='Query 1212.mn Mongolia Statistical API')
    parser.add_argument('query', nargs='*', help='Search query')
    parser.add_argument('--refresh', action='store_true', help='Refresh metadata from API')
    parser.add_argument('--list', action='store_true', help='List all available tables')
    parser.add_argument('--detailed', action='store_true', help='Fetch detailed data (slower)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.refresh:
        api = API1212()
        store = MetadataStore()
        store.refresh_metadata(api)
        print("\n✓ Metadata refresh complete")
        return

    if args.list:
        store = MetadataStore()
        tables = store.list_all_tables()

        if args.json:
            print(json.dumps(tables, indent=2, ensure_ascii=False))
        else:
            print(f"\nAvailable Tables ({len(tables)}):\n")
            for table in tables:
                print(f"  [{table['id']}] {table['name_en']}")
                if table['description']:
                    print(f"      {table['description'][:80]}...")
                print(f"      Unit: {table['unit']}, Frequency: {table['frequency']}")
                print()
        return

    if not args.query:
        parser.print_help()
        return

    query_text = ' '.join(args.query)
    result = query_data(query_text, detailed=args.detailed)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\nQuery: {result['query']}")
        print(f"Found {len(result['matched_tables'])} relevant table(s)\n")

        for i, table in enumerate(result['matched_tables'], 1):
            print(f"{i}. {table['name']}")
            print(f"   ID: {table['id']}")
            if table['description']:
                print(f"   Description: {table['description']}")
            print(f"   Unit: {table['unit']}")
            print(f"   Frequency: {table['frequency']}")
            print(f"   Last Updated: {table['last_updated']}")

            if 'data' in table:
                print(f"   Data: {json.dumps(table['data'], indent=2, ensure_ascii=False)[:200]}...")
            print()

        if 'message' in result:
            print(f"Note: {result['message']}")


if __name__ == '__main__':
    main()
