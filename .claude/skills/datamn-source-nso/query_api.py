#!/usr/bin/env python3
"""
1212.mn API Query Module
Handles queries to Mongolia's National Statistical Office open data API
NEW API: https://data.1212.mn/api/v1/
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import requests

# API Configuration
BASE_URL = "https://data.1212.mn/api/v1"
DEFAULT_LANG = "en"  # Language: 'en' for English, 'mn' for Mongolian

# Paths
SCRIPT_DIR = Path(__file__).parent
METADATA_DIR = SCRIPT_DIR / "metadata"
DB_PATH = METADATA_DIR / "tables.db"

# Schema version for detecting outdated databases
CURRENT_SCHEMA_VERSION = 2


class API1212:
    """Client for interacting with 1212.mn API (new v1 API)"""

    def __init__(self, language: str = DEFAULT_LANG):
        self.language = language
        self.base_path = f"{BASE_URL}/{language}/NSO"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; 1212mn-skill/2.0)',
            'Accept': 'application/json'
        })

    def _get(self, path: str) -> Any:
        """Make GET request to API"""
        url = f"{self.base_path}/{path}" if path else self.base_path + "/"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error querying API: {e}", file=sys.stderr)
            return None

    def get_sectors(self) -> Optional[List[Dict]]:
        """
        Get list of all main sectors
        Returns: List of {'id': str, 'type': str, 'text': str}
        """
        return self._get("")

    def get_subsectors(self, sector_id: str) -> Optional[List[Dict]]:
        """
        Get list of subsectors for a sector
        Args:
            sector_id: Sector ID (English name)
        Returns: List of {'id': str, 'type': str, 'text': str}
        """
        return self._get(f"{quote(sector_id)}/")

    def get_tables(self, sector_id: str, subsector_id: str) -> Optional[List[Dict]]:
        """
        Get list of tables in a subsector
        Args:
            sector_id: Sector ID (English name)
            subsector_id: Subsector ID
        Returns: List of {'id': str, 'type': str, 'text': str, 'updated': str}
        """
        return self._get(f"{quote(sector_id)}/{quote(subsector_id)}/")

    def get_data(self, sector_id: str, subsector_id: str, table_id: str) -> Optional[Dict]:
        """
        Get statistical data for a table
        Args:
            sector_id: Sector ID (English name)
            subsector_id: Subsector ID
            table_id: Table ID (e.g., 'DT_NSO_0300_001V2.px')
        Returns: Dict with 'title', 'variables' (list of variable definitions)
        """
        return self._get(f"{quote(sector_id)}/{quote(subsector_id)}/{quote(table_id)}")


class MetadataStore:
    """Manages local metadata cache in SQLite"""

    def __init__(self, db_path: Path = DB_PATH, auto_fix: bool = True):
        self.db_path = db_path
        self.auto_fix = auto_fix
        self._ensure_db()

    def _get_schema_version(self) -> int:
        """Get the current schema version from database"""
        if not self.db_path.exists():
            return 0

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            )
            if cursor.fetchone():
                cursor = conn.execute("SELECT version FROM schema_version ORDER BY updated_at DESC LIMIT 1")
                result = cursor.fetchone()
                version = result[0] if result else 0
            else:
                version = 0
            conn.close()
            return version
        except Exception:
            return 0

    def _set_schema_version(self, conn: sqlite3.Connection, version: int):
        """Set the schema version in database"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER,
                updated_at TEXT
            )
        """)
        conn.execute("DELETE FROM schema_version")
        conn.execute(
            "INSERT INTO schema_version (version, updated_at) VALUES (?, ?)",
            (version, datetime.now().isoformat())
        )
        conn.commit()

    def _verify_schema(self) -> tuple[bool, str]:
        """
        Verify the database schema matches expected structure
        Returns: (is_valid, error_message)
        """
        if not self.db_path.exists():
            return False, "Database file does not exist"

        try:
            conn = sqlite3.connect(self.db_path)

            # Check required tables exist
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('sectors', 'subsectors', 'tables', 'tables_fts')
            """)
            tables = {row[0] for row in cursor.fetchall()}
            required_tables = {'sectors', 'subsectors', 'tables', 'tables_fts'}

            if not required_tables.issubset(tables):
                missing = required_tables - tables
                conn.close()
                return False, f"Missing tables: {', '.join(missing)}"

            # Check sectors table schema
            cursor = conn.execute("PRAGMA table_info(sectors)")
            sector_cols = {row[1] for row in cursor.fetchall()}
            required_sector_cols = {'id', 'name_en', 'name_mn', 'type', 'updated_at'}

            if not required_sector_cols.issubset(sector_cols):
                missing = required_sector_cols - sector_cols
                conn.close()
                return False, f"Sectors table missing columns: {', '.join(missing)}"

            # Check subsectors table schema
            cursor = conn.execute("PRAGMA table_info(subsectors)")
            subsector_cols = {row[1] for row in cursor.fetchall()}
            required_subsector_cols = {'id', 'sector_id', 'name_en', 'name_mn', 'type', 'updated_at'}

            if not required_subsector_cols.issubset(subsector_cols):
                missing = required_subsector_cols - subsector_cols
                conn.close()
                return False, f"Subsectors table missing columns: {', '.join(missing)}"

            # Check tables table schema
            cursor = conn.execute("PRAGMA table_info(tables)")
            table_cols = {row[1] for row in cursor.fetchall()}
            required_table_cols = {'id', 'subsector_id', 'sector_id', 'name_en', 'name_mn',
                                   'type', 'last_updated', 'keywords', 'full_path', 'updated_at'}

            if not required_table_cols.issubset(table_cols):
                missing = required_table_cols - table_cols
                conn.close()
                return False, f"Tables table missing columns: {', '.join(missing)}"

            conn.close()
            return True, ""

        except Exception as e:
            return False, f"Schema verification error: {str(e)}"

    def _rebuild_database(self):
        """Delete old database and create fresh schema"""
        if self.db_path.exists():
            print(f"Removing outdated database: {self.db_path}")
            self.db_path.unlink()

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_fresh_schema()

    def _create_fresh_schema(self):
        """Create database with fresh schema"""
        conn = sqlite3.connect(self.db_path)

        # Create schema version table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER,
                updated_at TEXT
            )
        """)

        # Create sectors table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sectors (
                id TEXT PRIMARY KEY,
                name_en TEXT,
                name_mn TEXT,
                type TEXT,
                updated_at TEXT
            )
        """)

        # Create subsectors table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subsectors (
                id TEXT,
                sector_id TEXT,
                name_en TEXT,
                name_mn TEXT,
                type TEXT,
                updated_at TEXT,
                PRIMARY KEY (sector_id, id),
                FOREIGN KEY (sector_id) REFERENCES sectors(id)
            )
        """)

        # Create tables table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                id TEXT,
                subsector_id TEXT,
                sector_id TEXT,
                name_en TEXT,
                name_mn TEXT,
                type TEXT,
                last_updated TEXT,
                keywords TEXT,
                full_path TEXT,
                updated_at TEXT,
                PRIMARY KEY (sector_id, subsector_id, id)
            )
        """)

        # Create FTS index
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS tables_fts USING fts5(
                id,
                name_en,
                name_mn,
                keywords,
                full_path,
                content=tables,
                content_rowid=rowid
            )
        """)

        self._set_schema_version(conn, CURRENT_SCHEMA_VERSION)
        conn.commit()
        conn.close()

    def _ensure_db(self):
        """Create database and tables if they don't exist, or rebuild if schema is outdated"""
        # Check if database exists
        if not self.db_path.exists():
            print("Creating new metadata database...")
            self._create_fresh_schema()
            return

        # Check schema version
        current_version = self._get_schema_version()

        if current_version < CURRENT_SCHEMA_VERSION:
            if self.auto_fix:
                print(f"\n{'='*60}")
                print(f"SCHEMA MISMATCH DETECTED")
                print(f"{'='*60}")
                print(f"Database schema version: {current_version}")
                print(f"Expected schema version: {CURRENT_SCHEMA_VERSION}")
                print(f"\nAutomatically rebuilding database with current schema...")
                print(f"{'='*60}\n")
                self._rebuild_database()
                print("\nDatabase rebuilt successfully!")
                print("You need to refresh metadata by running:")
                print("  python3 query_api.py --refresh\n")
            else:
                print(f"\nWARNING: Database schema is outdated (version {current_version}, expected {CURRENT_SCHEMA_VERSION})")
                print("Run with --force-refresh to rebuild the database\n")
            return

        # Verify schema is correct
        is_valid, error_msg = self._verify_schema()

        if not is_valid:
            if self.auto_fix:
                print(f"\n{'='*60}")
                print(f"DATABASE SCHEMA ERROR")
                print(f"{'='*60}")
                print(f"Error: {error_msg}")
                print(f"\nAutomatically rebuilding database...")
                print(f"{'='*60}\n")
                self._rebuild_database()
                print("\nDatabase rebuilt successfully!")
                print("You need to refresh metadata by running:")
                print("  python3 query_api.py --refresh\n")
            else:
                raise Exception(f"Database schema error: {error_msg}\n"
                              f"Run: python3 query_api.py --force-refresh")

    def refresh_metadata(self, api: API1212):
        """Refresh all metadata from API"""
        print("Refreshing metadata from 1212.mn API...")
        conn = sqlite3.connect(self.db_path)
        now = datetime.now().isoformat()

        # Fetch and store sectors
        print("Fetching sectors...")
        sectors = api.get_sectors()
        if not sectors:
            print("ERROR: Could not fetch sectors from API")
            conn.close()
            return

        sector_count = 0
        for sector in sectors:
            sector_id = sector.get('id', '')
            conn.execute("""
                INSERT OR REPLACE INTO sectors (id, name_en, name_mn, type, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sector_id,
                sector_id,  # id is the English name
                sector.get('text', ''),  # text is the Mongolian name
                sector.get('type', ''),
                now
            ))
            sector_count += 1
        conn.commit()
        print(f"  ✓ Stored {sector_count} sectors")

        # Fetch subsectors for each sector
        print("Fetching subsectors...")
        subsector_count = 0
        for sector in sectors:
            sector_id = sector.get('id', '')
            if not sector_id:
                continue

            subsectors = api.get_subsectors(sector_id)
            if subsectors:
                for subsector in subsectors:
                    subsector_id = subsector.get('id', '')
                    conn.execute("""
                        INSERT OR REPLACE INTO subsectors
                        (id, sector_id, name_en, name_mn, type, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        subsector_id,
                        sector_id,
                        subsector_id,
                        subsector.get('text', ''),
                        subsector.get('type', ''),
                        now
                    ))
                    subsector_count += 1
        conn.commit()
        print(f"  ✓ Stored {subsector_count} subsectors")

        # Fetch tables for each subsector
        print("Fetching tables (this may take a while)...")
        table_count = 0
        cursor = conn.execute("SELECT sector_id, id FROM subsectors")
        subsector_pairs = cursor.fetchall()

        for sector_id, subsector_id in subsector_pairs:
            tables = api.get_tables(sector_id, subsector_id)
            if tables:
                for table in tables:
                    table_id = table.get('id', '')
                    name_mn = table.get('text', '')

                    # Extract English name from Mongolian (basic heuristic)
                    # In practice, we'll use the table_id as the identifier
                    name_en = table_id

                    # Generate keywords
                    keywords = self._extract_keywords(name_en, name_mn)

                    # Build full path for API access
                    full_path = f"{sector_id}/{subsector_id}/{table_id}"

                    conn.execute("""
                        INSERT OR REPLACE INTO tables
                        (id, subsector_id, sector_id, name_en, name_mn, type,
                         last_updated, keywords, full_path, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        table_id,
                        subsector_id,
                        sector_id,
                        name_en,
                        name_mn,
                        table.get('type', ''),
                        table.get('updated', ''),
                        keywords,
                        full_path,
                        now
                    ))
                    table_count += 1

                    if table_count % 10 == 0:
                        print(f"    {table_count} tables processed...", end='\r')

        # Update FTS index
        conn.execute("INSERT INTO tables_fts(tables_fts) VALUES('rebuild')")

        # Update schema version
        self._set_schema_version(conn, CURRENT_SCHEMA_VERSION)

        conn.commit()
        conn.close()
        print(f"\n  ✓ Stored {table_count} tables")
        print(f"\nMetadata refresh completed at {now}")
        print(f"Total: {sector_count} sectors, {subsector_count} subsectors, {table_count} tables")

    def _extract_keywords(self, name_en: str, name_mn: str) -> str:
        """Extract searchable keywords from names"""
        # Combine and lowercase
        text = f"{name_en} {name_mn}".lower()

        # Common English-Mongolian term mappings
        # These are common statistical terms
        keyword_map = {
            'population': ['хүн ам', 'inhabitants', 'residents', 'demographic'],
            'household': ['өрх', 'family', 'dwelling'],
            'employment': ['ажил эрхлэлт', 'хөдөлмөр', 'job', 'work', 'labor'],
            'unemployment': ['ажилгүйдэл', 'jobless'],
            'income': ['орлого', 'earnings', 'salary', 'wage'],
            'gdp': ['дотоод нийт бүтээгдэхүүн', 'economy', 'gross domestic product'],
            'price': ['үнэ', 'cost', 'value', 'rate'],
            'apartment': ['орон сууц', 'housing', 'residential', 'dwelling', 'home'],
            'district': ['дүүрэг', 'region', 'area', 'zone'],
            'average': ['дундаж', 'mean', 'typical'],
            'education': ['боловсрол', 'school', 'learning'],
            'health': ['эрүүл мэнд', 'medical', 'healthcare'],
            'trade': ['худалдаа', 'commerce', 'export', 'import'],
            'agriculture': ['хөдөө аж ахуй', 'farming', 'livestock'],
        }

        keywords = set()

        # Add all words from the text
        for word in text.split():
            if len(word) > 2:
                keywords.add(word.strip('.,;:()[]{}'))

        # Add mapped keywords
        for eng, related in keyword_map.items():
            if eng in text:
                keywords.add(eng)
                keywords.update(related)
            for rel in related:
                if rel in text:
                    keywords.add(eng)
                    keywords.update(related)

        return ' '.join(sorted(keywords))

    def search_tables(self, query: str, limit: int = 10) -> List[Dict]:
        """Search tables using full-text search"""
        try:
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

        except sqlite3.OperationalError as e:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"DATABASE ERROR", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            print(f"\nThe database schema appears to be corrupted or outdated.", file=sys.stderr)
            print(f"Please rebuild the database by running:", file=sys.stderr)
            print(f"  python3 query_api.py --force-refresh", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Search error: {e}", file=sys.stderr)
            return []

    def get_table_by_id(self, table_id: str) -> Optional[Dict]:
        """Get table by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("SELECT * FROM tables WHERE id = ?", (table_id,))
        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def list_all_tables(self, sector: Optional[str] = None) -> List[Dict]:
        """List all tables in the database, optionally filtered by sector"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            if sector:
                cursor = conn.execute("""
                    SELECT id, sector_id, subsector_id, name_en, name_mn, last_updated, full_path
                    FROM tables
                    WHERE sector_id = ?
                    ORDER BY name_mn
                """, (sector,))
            else:
                cursor = conn.execute("""
                    SELECT id, sector_id, subsector_id, name_en, name_mn, last_updated, full_path
                    FROM tables
                    ORDER BY sector_id, subsector_id, name_mn
                """)

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results

        except sqlite3.OperationalError as e:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"DATABASE ERROR", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            print(f"\nThe database schema appears to be corrupted or outdated.", file=sys.stderr)
            print(f"Please rebuild the database by running:", file=sys.stderr)
            print(f"  python3 query_api.py --force-refresh", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)
            return []


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

    # Check if metadata exists and has data
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("SELECT COUNT(*) FROM tables")
        table_count = cursor.fetchone()[0]
        conn.close()

        if table_count == 0:
            return {
                'error': 'Metadata database is empty',
                'message': 'The database schema has been initialized but contains no data.\n'
                          'Please refresh metadata by running:\n'
                          '  python3 query_api.py --refresh'
            }
    except Exception as e:
        return {
            'error': 'Database error',
            'message': f'Error accessing database: {str(e)}\n'
                      'Try rebuilding the database:\n'
                      '  python3 query_api.py --force-refresh'
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
            'name_en': table['name_en'],
            'name_mn': table['name_mn'],
            'sector': table['sector_id'],
            'subsector': table['subsector_id'],
            'last_updated': table['last_updated'],
            'full_path': table['full_path']
        }

        # If detailed, fetch actual data
        if detailed:
            print(f"  Fetching data for: {table['name_mn']}...")
            data = api.get_data(table['sector_id'], table['subsector_id'], table['id'])
            if data:
                table_info['data'] = data
                table_info['title'] = data.get('title', '')
                table_info['variables'] = data.get('variables', [])

        result['matched_tables'].append(table_info)

    return result


def main():
    """CLI interface for the API"""
    import argparse

    parser = argparse.ArgumentParser(description='Query 1212.mn Mongolia Statistical API (v1)')
    parser.add_argument('query', nargs='*', help='Search query')
    parser.add_argument('--refresh', action='store_true', help='Refresh metadata from API')
    parser.add_argument('--force-refresh', action='store_true',
                        help='Force rebuild database and refresh metadata (use if schema errors occur)')
    parser.add_argument('--list', action='store_true', help='List all available tables')
    parser.add_argument('--sectors', action='store_true', help='List all sectors')
    parser.add_argument('--sector', type=str, help='Filter by sector')
    parser.add_argument('--detailed', action='store_true', help='Fetch detailed data (slower)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--lang', type=str, default=DEFAULT_LANG, choices=['en', 'mn'],
                        help='Language (en or mn)')

    args = parser.parse_args()

    # Handle force refresh
    if args.force_refresh:
        print("Force refresh: Rebuilding database and refreshing all metadata...")
        api = API1212(language=args.lang)
        # Create store with auto_fix disabled to trigger manual rebuild
        if DB_PATH.exists():
            print(f"Deleting existing database: {DB_PATH}")
            DB_PATH.unlink()
        store = MetadataStore()
        store.refresh_metadata(api)
        print("\nForce refresh complete!")
        return

    # Handle regular refresh
    if args.refresh:
        api = API1212(language=args.lang)
        store = MetadataStore()
        store.refresh_metadata(api)
        print("\nMetadata refresh complete")
        return

    if args.sectors:
        api = API1212(language=args.lang)
        sectors = api.get_sectors()

        if args.json:
            print(json.dumps(sectors, indent=2, ensure_ascii=False))
        else:
            print(f"\nAvailable Sectors ({len(sectors) if sectors else 0}):\n")
            if sectors:
                for sector in sectors:
                    print(f"  [{sector['id']}]")
                    print(f"      EN: {sector['id']}")
                    print(f"      MN: {sector['text']}")
                    print()
        return

    if args.list:
        store = MetadataStore()
        tables = store.list_all_tables(sector=args.sector)

        if args.json:
            print(json.dumps(tables, indent=2, ensure_ascii=False))
        else:
            filter_msg = f" in sector '{args.sector}'" if args.sector else ""
            print(f"\nAvailable Tables{filter_msg} ({len(tables)}):\n")
            for table in tables[:50]:  # Show first 50
                print(f"  [{table['id']}]")
                print(f"      Sector: {table['sector_id']}")
                print(f"      Subsector: {table['subsector_id']}")
                print(f"      Name (MN): {table['name_mn']}")
                print(f"      Updated: {table['last_updated']}")
                print()
            if len(tables) > 50:
                print(f"\n  ... and {len(tables) - 50} more tables")
                print("  Use --json flag to see all results")
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
            print(f"{i}. {table['name_mn']}")
            print(f"   ID: {table['id']}")
            print(f"   Sector: {table['sector']}")
            print(f"   Subsector: {table['subsector']}")
            print(f"   Last Updated: {table['last_updated']}")

            if 'title' in table:
                print(f"   Title: {table['title']}")

            if 'variables' in table:
                print(f"   Variables:")
                for var in table['variables'][:3]:  # Show first 3 variables
                    print(f"      - {var['text']}: {len(var['values'])} values")
                if len(table['variables']) > 3:
                    print(f"      ... and {len(table['variables']) - 3} more variables")

            print()

        if 'message' in result:
            print(f"Note: {result['message']}")


if __name__ == '__main__':
    main()
