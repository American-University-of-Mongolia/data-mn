#!/usr/bin/env python3
"""
Data.mn Registry Module

Manages the central registry of data sources, datasets, and versions.
"""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "data.db"
SCHEMA_PATH = SCRIPT_DIR / "schema.sql"


@dataclass
class Source:
    """Represents a data source"""
    id: str
    name: str
    type: str
    definition_path: str
    name_mn: Optional[str] = None
    base_url: Optional[str] = None
    update_frequency: str = "unknown"
    enabled: bool = True
    priority: int = 50
    config: Optional[Dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Dataset:
    """Represents a tracked dataset"""
    id: str
    source_id: str
    name_en: str
    category_en: str
    definition_path: str
    category_mn: Optional[str] = None
    # Parent/Split relationship
    parent_id: Optional[str] = None  # If this is a split, references parent dataset
    is_parent: bool = False  # True if this dataset has splits defined
    split_filter: Optional[Dict] = None  # Filter criteria for splits
    # Metadata
    name_mn: Optional[str] = None
    description_en: Optional[str] = None
    description_mn: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    keywords_en: List[str] = field(default_factory=list)
    keywords_mn: List[str] = field(default_factory=list)
    source_ref: Optional[str] = None
    source_path: Optional[str] = None
    source_metadata: Optional[Dict] = None
    current_version: int = 0
    status: str = "pending"
    data_file: Optional[str] = None
    mdx_file_en: Optional[str] = None
    mdx_file_mn: Optional[str] = None
    chart_spec: Optional[str] = None
    data_as_of: Optional[str] = None
    source_updated_at: Optional[str] = None
    last_checked_at: Optional[str] = None
    last_fetched_at: Optional[str] = None
    auto_update: bool = True
    auto_publish: bool = True
    # URL Stability (see docs/principles/url-stability.md)
    canonical_slug: Optional[str] = None  # Permanent URL slug
    first_published_at: Optional[str] = None  # When URL first went live
    is_published: bool = False  # Whether currently published
    deprecated_at: Optional[str] = None  # When marked deprecated
    deprecation_reason: Optional[str] = None  # Why deprecated
    successor_id: Optional[str] = None  # Replacement dataset
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class URLRedirect:
    """Represents a URL redirect for URL stability"""
    id: int
    old_slug: str
    target_dataset_id: Optional[str] = None
    target_url: Optional[str] = None
    redirect_type: int = 301
    reason: Optional[str] = None
    created_at: Optional[str] = None
    hit_count: int = 0
    last_hit_at: Optional[str] = None


@dataclass
class Version:
    """Represents a dataset version"""
    id: int
    dataset_id: str
    version: int
    data_hash: str
    data_path: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    change_type: Optional[str] = None
    change_summary: Optional[str] = None
    diff_stats: Optional[Dict] = None
    source_updated_at: Optional[str] = None
    source_raw_files: Optional[List[str]] = None
    fetched_at: Optional[str] = None


class Registry:
    """Registry database interface"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Ensure database exists with correct schema"""
        if not self.db_path.exists():
            if SCHEMA_PATH.exists():
                conn = sqlite3.connect(self.db_path)
                with open(SCHEMA_PATH, 'r') as f:
                    conn.executescript(f.read())
                conn.close()
            else:
                raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ============ Sources ============

    def add_source(self, source: Source) -> None:
        """Add a new data source"""
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO sources (id, name, name_mn, type, base_url, definition_path,
                                update_frequency, enabled, priority, config)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source.id, source.name, source.name_mn, source.type, source.base_url,
            source.definition_path, source.update_frequency, source.enabled,
            source.priority, json.dumps(source.config) if source.config else None
        ))
        conn.commit()
        conn.close()

    def get_source(self, source_id: str) -> Optional[Source]:
        """Get a source by ID"""
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        conn.close()
        if row:
            return Source(
                id=row['id'],
                name=row['name'],
                name_mn=row['name_mn'],
                type=row['type'],
                base_url=row['base_url'],
                definition_path=row['definition_path'],
                update_frequency=row['update_frequency'],
                enabled=bool(row['enabled']),
                priority=row['priority'],
                config=json.loads(row['config']) if row['config'] else None,
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        return None

    def list_sources(self, enabled_only: bool = False) -> List[Source]:
        """List all sources"""
        conn = self._get_conn()
        query = "SELECT * FROM sources"
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY priority, name"
        rows = conn.execute(query).fetchall()
        conn.close()
        return [Source(
            id=r['id'], name=r['name'], name_mn=r['name_mn'], type=r['type'],
            base_url=r['base_url'], definition_path=r['definition_path'],
            update_frequency=r['update_frequency'], enabled=bool(r['enabled']),
            priority=r['priority'],
            config=json.loads(r['config']) if r['config'] else None,
            created_at=r['created_at'], updated_at=r['updated_at']
        ) for r in rows]

    # ============ Datasets ============

    def add_dataset(self, dataset: Dataset) -> None:
        """Add a new dataset"""
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO datasets (id, source_id, parent_id, is_parent, split_filter,
                                 name_en, name_mn, description_en,
                                 description_mn, category_en, category_mn, tags, keywords_en, keywords_mn,
                                 source_ref, source_path, definition_path, source_metadata,
                                 status, auto_update, auto_publish)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset.id, dataset.source_id, dataset.parent_id, dataset.is_parent,
            json.dumps(dataset.split_filter) if dataset.split_filter else None,
            dataset.name_en, dataset.name_mn,
            dataset.description_en, dataset.description_mn,
            dataset.category_en, dataset.category_mn,
            json.dumps(dataset.tags), json.dumps(dataset.keywords_en),
            json.dumps(dataset.keywords_mn), dataset.source_ref, dataset.source_path,
            dataset.definition_path,
            json.dumps(dataset.source_metadata) if dataset.source_metadata else None,
            dataset.status, dataset.auto_update, dataset.auto_publish
        ))
        conn.commit()
        conn.close()

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get a dataset by ID"""
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
        conn.close()
        if row:
            return self._row_to_dataset(row)
        return None

    def list_datasets(self, source_id: Optional[str] = None,
                      status: Optional[str] = None,
                      category: Optional[str] = None,
                      parents_only: bool = False,
                      exclude_splits: bool = False) -> List[Dataset]:
        """List datasets with optional filtering

        Args:
            source_id: Filter by source
            status: Filter by status
            category: Filter by category
            parents_only: Only return datasets with is_parent=1
            exclude_splits: Exclude datasets that are splits (have parent_id)
        """
        conn = self._get_conn()
        query = "SELECT * FROM datasets WHERE 1=1"
        params = []
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        if category:
            query += " AND category_en = ?"
            params.append(category)
        if parents_only:
            query += " AND is_parent = 1"
        if exclude_splits:
            query += " AND parent_id IS NULL"
        query += " ORDER BY category_en, name_en"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [self._row_to_dataset(r) for r in rows]

    def get_splits(self, parent_id: str) -> List[Dataset]:
        """Get all split datasets for a parent dataset"""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM datasets WHERE parent_id = ? ORDER BY id",
            (parent_id,)
        ).fetchall()
        conn.close()
        return [self._row_to_dataset(r) for r in rows]

    def get_updatable_datasets(self) -> List[Dataset]:
        """Get datasets that should be checked for updates.

        Returns parent datasets and standalone datasets (not splits).
        Splits are updated when their parent is updated.
        """
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT * FROM datasets
            WHERE auto_update = 1
              AND parent_id IS NULL
            ORDER BY source_id, id
        """).fetchall()
        conn.close()
        return [self._row_to_dataset(r) for r in rows]

    def update_dataset(self, dataset_id: str, **kwargs) -> None:
        """Update dataset fields"""
        conn = self._get_conn()
        set_parts = []
        values = []
        for key, value in kwargs.items():
            if key in ['tags', 'keywords_en', 'keywords_mn', 'source_metadata', 'diff_stats']:
                value = json.dumps(value) if value else None
            set_parts.append(f"{key} = ?")
            values.append(value)
        values.append(dataset_id)
        query = f"UPDATE datasets SET {', '.join(set_parts)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()

    def _row_to_dataset(self, row) -> Dataset:
        """Convert database row to Dataset object"""
        keys = row.keys()
        return Dataset(
            id=row['id'],
            source_id=row['source_id'],
            parent_id=row['parent_id'] if 'parent_id' in keys else None,
            is_parent=bool(row['is_parent']) if 'is_parent' in keys else False,
            split_filter=json.loads(row['split_filter']) if ('split_filter' in keys and row['split_filter']) else None,
            name_en=row['name_en'],
            name_mn=row['name_mn'],
            description_en=row['description_en'],
            description_mn=row['description_mn'],
            category_en=row['category_en'],
            category_mn=row['category_mn'] if 'category_mn' in keys else None,
            tags=json.loads(row['tags']) if row['tags'] else [],
            keywords_en=json.loads(row['keywords_en']) if row['keywords_en'] else [],
            keywords_mn=json.loads(row['keywords_mn']) if row['keywords_mn'] else [],
            source_ref=row['source_ref'],
            source_path=row['source_path'],
            definition_path=row['definition_path'],
            source_metadata=json.loads(row['source_metadata']) if row['source_metadata'] else None,
            current_version=row['current_version'],
            status=row['status'],
            data_file=row['data_file'],
            mdx_file_en=row['mdx_file_en'],
            mdx_file_mn=row['mdx_file_mn'],
            chart_spec=row['chart_spec'],
            data_as_of=row['data_as_of'],
            source_updated_at=row['source_updated_at'],
            last_checked_at=row['last_checked_at'],
            last_fetched_at=row['last_fetched_at'],
            auto_update=bool(row['auto_update']),
            auto_publish=bool(row['auto_publish']),
            # URL Stability fields
            canonical_slug=row['canonical_slug'] if 'canonical_slug' in keys else None,
            first_published_at=row['first_published_at'] if 'first_published_at' in keys else None,
            is_published=bool(row['is_published']) if 'is_published' in keys else False,
            deprecated_at=row['deprecated_at'] if 'deprecated_at' in keys else None,
            deprecation_reason=row['deprecation_reason'] if 'deprecation_reason' in keys else None,
            successor_id=row['successor_id'] if 'successor_id' in keys else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    # ============ Versions ============

    def add_version(self, version: Version) -> int:
        """Add a new version, returns version ID"""
        conn = self._get_conn()
        cursor = conn.execute("""
            INSERT INTO versions (dataset_id, version, data_hash, data_path, row_count,
                                 column_count, change_type, change_summary, diff_stats,
                                 source_updated_at, source_raw_files)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version.dataset_id, version.version, version.data_hash, version.data_path,
            version.row_count, version.column_count, version.change_type,
            version.change_summary,
            json.dumps(version.diff_stats) if version.diff_stats else None,
            version.source_updated_at,
            json.dumps(version.source_raw_files) if version.source_raw_files else None
        ))
        version_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return version_id

    def get_versions(self, dataset_id: str, limit: int = 10) -> List[Version]:
        """Get version history for a dataset"""
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT * FROM versions WHERE dataset_id = ?
            ORDER BY version DESC LIMIT ?
        """, (dataset_id, limit)).fetchall()
        conn.close()
        return [Version(
            id=r['id'], dataset_id=r['dataset_id'], version=r['version'],
            data_hash=r['data_hash'], data_path=r['data_path'],
            row_count=r['row_count'], column_count=r['column_count'],
            change_type=r['change_type'], change_summary=r['change_summary'],
            diff_stats=json.loads(r['diff_stats']) if r['diff_stats'] else None,
            source_updated_at=r['source_updated_at'],
            source_raw_files=json.loads(r['source_raw_files']) if r['source_raw_files'] else None,
            fetched_at=r['fetched_at']
        ) for r in rows]

    # ============ Activity Log ============

    def log_activity(self, action: str, status: str, message: str = None,
                     dataset_id: str = None, source_id: str = None,
                     details: Dict = None, triggered_by: str = "manual") -> None:
        """Log an activity"""
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO activity_log (action, dataset_id, source_id, status, message,
                                      details, triggered_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            action, dataset_id, source_id, status, message,
            json.dumps(details) if details else None, triggered_by
        ))
        conn.commit()
        conn.close()

    def get_recent_activity(self, limit: int = 20, dataset_id: str = None) -> List[Dict]:
        """Get recent activity log entries"""
        conn = self._get_conn()
        query = "SELECT * FROM activity_log"
        params = []
        if dataset_id:
            query += " WHERE dataset_id = ?"
            params.append(dataset_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ============ Status ============

    def get_status(self) -> Dict[str, Any]:
        """Get overall registry status"""
        conn = self._get_conn()

        # Count sources
        source_counts = conn.execute("""
            SELECT enabled, COUNT(*) as count FROM sources GROUP BY enabled
        """).fetchall()
        sources = {'enabled': 0, 'disabled': 0, 'total': 0}
        for row in source_counts:
            if row['enabled']:
                sources['enabled'] = row['count']
            else:
                sources['disabled'] = row['count']
        sources['total'] = sources['enabled'] + sources['disabled']

        # Count datasets by status
        dataset_counts = conn.execute("""
            SELECT status, COUNT(*) as count FROM datasets GROUP BY status
        """).fetchall()
        datasets = {r['status']: r['count'] for r in dataset_counts}
        datasets['total'] = sum(datasets.values())

        # Count datasets by category
        category_counts = conn.execute("""
            SELECT category_en, COUNT(*) as count FROM datasets GROUP BY category_en
        """).fetchall()
        categories = {r['category_en']: r['count'] for r in category_counts}

        # Recent activity
        recent = conn.execute("""
            SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 5
        """).fetchall()

        # Datasets needing update (status = 'outdated')
        outdated = conn.execute("""
            SELECT id, name_en, source_id FROM datasets WHERE status = 'outdated'
        """).fetchall()

        conn.close()

        return {
            'sources': sources,
            'datasets': datasets,
            'categories': categories,
            'recent_activity': [dict(r) for r in recent],
            'outdated_datasets': [dict(r) for r in outdated]
        }

    # ============ URL Stability ============
    # See docs/principles/url-stability.md for full documentation

    def publish_dataset(self, dataset_id: str, canonical_slug: str = None) -> bool:
        """Mark a dataset as published and assign canonical URL.

        Args:
            dataset_id: The dataset ID to publish
            canonical_slug: Custom URL slug (defaults to dataset_id)

        Returns:
            True if published, False if skipped (parent dataset)

        Raises:
            ValueError: If dataset not found or slug already in use
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")

        # Parent datasets don't have MDX pages and shouldn't be published
        if dataset.is_parent:
            return False  # Silently skip - caller can check return value

        slug = canonical_slug or dataset_id

        # Check slug isn't already used by another dataset
        conn = self._get_conn()
        existing = conn.execute(
            "SELECT id FROM datasets WHERE canonical_slug = ? AND id != ?",
            (slug, dataset_id)
        ).fetchone()
        conn.close()

        if existing:
            raise ValueError(f"Slug '{slug}' already in use by: {existing['id']}")

        # Set publication fields
        now = datetime.now().isoformat()
        update_fields = {
            'canonical_slug': slug,
            'is_published': True
        }

        # Only set first_published_at if not already set
        if not dataset.first_published_at:
            update_fields['first_published_at'] = now

        self.update_dataset(dataset_id, **update_fields)
        self.log_activity('publish', 'success',
                         f"Published dataset with slug: {slug}",
                         dataset_id=dataset_id)
        return True

    def rename_slug(self, dataset_id: str, new_slug: str, reason: str) -> None:
        """Rename a dataset's URL slug, creating redirect from old slug.

        Args:
            dataset_id: The dataset ID to rename
            new_slug: The new URL slug
            reason: Why the rename is needed (required for audit)

        Raises:
            ValueError: If dataset not published or new slug in use
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")
        if not dataset.canonical_slug:
            raise ValueError("Dataset must be published first (no canonical_slug)")

        old_slug = dataset.canonical_slug

        if old_slug == new_slug:
            raise ValueError("New slug is same as current slug")

        # Check new slug isn't already used
        conn = self._get_conn()
        existing = conn.execute(
            "SELECT id FROM datasets WHERE canonical_slug = ? AND id != ?",
            (new_slug, dataset_id)
        ).fetchone()
        conn.close()

        if existing:
            raise ValueError(f"Slug '{new_slug}' already in use by: {existing['id']}")

        # Create redirect from old slug
        self.add_redirect(old_slug, target_dataset_id=dataset_id,
                         reason=f"Renamed from {old_slug}: {reason}")

        # Update to new slug
        self.update_dataset(dataset_id, canonical_slug=new_slug)
        self.log_activity('rename', 'success',
                         f"Renamed slug: {old_slug} → {new_slug}",
                         dataset_id=dataset_id)

    def deprecate_dataset(self, dataset_id: str, reason: str,
                          successor_id: str = None) -> None:
        """Mark a dataset as deprecated.

        Args:
            dataset_id: The dataset ID to deprecate
            reason: Why the dataset is deprecated (required)
            successor_id: Optional replacement dataset ID
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")

        if successor_id:
            successor = self.get_dataset(successor_id)
            if not successor:
                raise ValueError(f"Successor dataset not found: {successor_id}")

        now = datetime.now().isoformat()
        self.update_dataset(dataset_id,
                           deprecated_at=now,
                           deprecation_reason=reason,
                           successor_id=successor_id)

        msg = f"Deprecated: {reason}"
        if successor_id:
            msg += f" (successor: {successor_id})"

        self.log_activity('deprecate', 'success', msg, dataset_id=dataset_id)

    def add_redirect(self, old_slug: str, target_dataset_id: str = None,
                     target_url: str = None, redirect_type: int = 301,
                     reason: str = None) -> int:
        """Add a URL redirect.

        Args:
            old_slug: The URL slug being redirected FROM
            target_dataset_id: Dataset ID to redirect TO (uses canonical_slug)
            target_url: Full URL if redirecting externally
            redirect_type: HTTP redirect code (301 or 302)
            reason: Why redirect exists (for audit)

        Returns:
            ID of the created redirect
        """
        if not target_dataset_id and not target_url:
            raise ValueError("Must provide target_dataset_id or target_url")

        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                INSERT INTO url_redirects (old_slug, target_dataset_id, target_url,
                                          redirect_type, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (old_slug, target_dataset_id, target_url, redirect_type, reason))
            redirect_id = cursor.lastrowid
            conn.commit()
            return redirect_id
        except sqlite3.IntegrityError:
            raise ValueError(f"Redirect already exists for slug: {old_slug}")
        finally:
            conn.close()

    def get_redirect(self, old_slug: str) -> Optional[URLRedirect]:
        """Get a redirect by old slug."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM url_redirects WHERE old_slug = ?",
            (old_slug,)
        ).fetchone()
        conn.close()

        if row:
            return URLRedirect(
                id=row['id'],
                old_slug=row['old_slug'],
                target_dataset_id=row['target_dataset_id'],
                target_url=row['target_url'],
                redirect_type=row['redirect_type'],
                reason=row['reason'],
                created_at=row['created_at'],
                hit_count=row['hit_count'],
                last_hit_at=row['last_hit_at']
            )
        return None

    def list_redirects(self) -> List[URLRedirect]:
        """List all URL redirects."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM url_redirects ORDER BY created_at DESC"
        ).fetchall()
        conn.close()

        return [URLRedirect(
            id=r['id'],
            old_slug=r['old_slug'],
            target_dataset_id=r['target_dataset_id'],
            target_url=r['target_url'],
            redirect_type=r['redirect_type'],
            reason=r['reason'],
            created_at=r['created_at'],
            hit_count=r['hit_count'],
            last_hit_at=r['last_hit_at']
        ) for r in rows]

    def export_redirects_for_astro(self) -> Dict[str, str]:
        """Export redirects as a dict for Astro config.

        Returns dict mapping old URLs to new URLs for both /en/ and /mn/ paths.
        """
        redirects = {}
        conn = self._get_conn()

        # Get explicit redirects
        rows = conn.execute("""
            SELECT r.old_slug, r.target_dataset_id, r.target_url, d.canonical_slug
            FROM url_redirects r
            LEFT JOIN datasets d ON r.target_dataset_id = d.id
        """).fetchall()

        for row in rows:
            old_slug = row['old_slug']
            if row['target_url']:
                # External redirect
                target = row['target_url']
            elif row['canonical_slug']:
                # Internal redirect to dataset
                target = f"/data/{row['canonical_slug']}"
            else:
                continue

            # Add both language versions
            redirects[f"/en/data/{old_slug}"] = f"/en{target}" if not target.startswith('http') else target
            redirects[f"/mn/data/{old_slug}"] = f"/mn{target}" if not target.startswith('http') else target

        conn.close()
        return redirects

    def get_published_datasets(self) -> List[Dataset]:
        """Get all published datasets."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM datasets WHERE is_published = 1 ORDER BY canonical_slug"
        ).fetchall()
        conn.close()
        return [self._row_to_dataset(r) for r in rows]

    def get_deprecated_datasets(self) -> List[Dataset]:
        """Get all deprecated datasets."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM datasets WHERE deprecated_at IS NOT NULL ORDER BY deprecated_at DESC"
        ).fetchall()
        conn.close()
        return [self._row_to_dataset(r) for r in rows]


# ============ CLI ============

def print_status(registry: Registry):
    """Print registry status"""
    status = registry.get_status()

    print("\n" + "=" * 60)
    print("DATA.MN REGISTRY STATUS")
    print("=" * 60)

    print(f"\nSources: {status['sources']['total']} total "
          f"({status['sources']['enabled']} enabled, {status['sources']['disabled']} disabled)")

    print(f"\nDatasets: {status['datasets'].get('total', 0)} total")
    for s, count in status['datasets'].items():
        if s != 'total':
            print(f"  - {s}: {count}")

    if status['categories']:
        print("\nBy Category:")
        for cat, count in sorted(status['categories'].items()):
            print(f"  - {cat}: {count}")

    if status['outdated_datasets']:
        print("\nNeeding Update:")
        for d in status['outdated_datasets']:
            print(f"  - {d['id']} ({d['source_id']})")

    if status['recent_activity']:
        print("\nRecent Activity:")
        for a in status['recent_activity'][:5]:
            print(f"  [{a['timestamp']}] {a['action']}: {a['status']} - {a.get('message', '')}")

    print()


def print_sources(registry: Registry):
    """Print all sources"""
    sources = registry.list_sources()
    print(f"\nData Sources ({len(sources)}):\n")
    for s in sources:
        status = "enabled" if s.enabled else "disabled"
        print(f"  [{s.id}] {s.name}")
        print(f"      Type: {s.type}, Frequency: {s.update_frequency}, Status: {status}")
        print(f"      Definition: {s.definition_path}")
        print()


def print_datasets(registry: Registry, source_id: str = None, status: str = None):
    """Print datasets"""
    datasets = registry.list_datasets(source_id=source_id, status=status)
    print(f"\nDatasets ({len(datasets)}):\n")
    for d in datasets:
        # Show relationship indicator
        if d.is_parent:
            prefix = "📦"  # Parent dataset
        elif d.parent_id:
            prefix = "  └─"  # Split dataset
        else:
            prefix = "📄"  # Standalone
        print(f"  {prefix} [{d.id}] {d.name_en}")
        print(f"      Source: {d.source_id}, Category: {d.category_en}")
        print(f"      Status: {d.status}, Version: {d.current_version}")
        if d.parent_id:
            print(f"      Parent: {d.parent_id}")
        if d.is_parent:
            splits = registry.get_splits(d.id)
            if splits:
                print(f"      Splits: {', '.join(s.id for s in splits)}")
        if d.last_fetched_at:
            print(f"      Last Fetched: {d.last_fetched_at}")
        print()


def print_info(registry: Registry, dataset_id: str):
    """Print detailed dataset info"""
    dataset = registry.get_dataset(dataset_id)
    if not dataset:
        print(f"Dataset not found: {dataset_id}")
        return

    print(f"\n{'=' * 60}")
    print(f"Dataset: {dataset.id}")
    print(f"{'=' * 60}")
    print(f"\nName (EN): {dataset.name_en}")
    print(f"Name (MN): {dataset.name_mn or 'N/A'}")
    print(f"Source: {dataset.source_id}")
    print(f"Category (EN): {dataset.category_en}")
    print(f"Category (MN): {dataset.category_mn or 'N/A'}")
    print(f"Status: {dataset.status}")
    print(f"Version: {dataset.current_version}")

    # Parent/Split info
    if dataset.is_parent:
        print(f"\nType: Parent Dataset (has splits)")
        splits = registry.get_splits(dataset.id)
        if splits:
            print(f"Splits ({len(splits)}):")
            for s in splits:
                print(f"  - {s.id}: {s.name_en}")
    elif dataset.parent_id:
        print(f"\nType: Split Dataset")
        print(f"Parent: {dataset.parent_id}")
        if dataset.split_filter:
            print(f"Filter: {json.dumps(dataset.split_filter)}")
    else:
        print(f"\nType: Standalone Dataset")

    print(f"\nDefinition: {dataset.definition_path}")
    if dataset.source_ref:
        print(f"Source Ref: {dataset.source_ref}")
    print(f"\nFiles:")
    print(f"  Data: {dataset.data_file or 'N/A'}")
    print(f"  MDX (EN): {dataset.mdx_file_en or 'N/A'}")
    print(f"  MDX (MN): {dataset.mdx_file_mn or 'N/A'}")
    print(f"  Chart: {dataset.chart_spec or 'N/A'}")
    print(f"\nTiming:")
    print(f"  Data As Of: {dataset.data_as_of or 'N/A'}")
    print(f"  Source Updated: {dataset.source_updated_at or 'N/A'}")
    print(f"  Last Checked: {dataset.last_checked_at or 'N/A'}")
    print(f"  Last Fetched: {dataset.last_fetched_at or 'N/A'}")

    # URL Stability info
    print(f"\nURL Stability:")
    print(f"  Canonical Slug: {dataset.canonical_slug or 'Not published'}")
    print(f"  Published: {'Yes' if dataset.is_published else 'No'}")
    if dataset.first_published_at:
        print(f"  First Published: {dataset.first_published_at}")
    if dataset.deprecated_at:
        print(f"  Deprecated: {dataset.deprecated_at}")
        print(f"  Reason: {dataset.deprecation_reason or 'N/A'}")
        if dataset.successor_id:
            print(f"  Successor: {dataset.successor_id}")

    # Version history
    versions = registry.get_versions(dataset_id)
    if versions:
        print(f"\nVersion History:")
        for v in versions:
            print(f"  v{v.version}: {v.change_type or 'N/A'} - {v.change_summary or 'N/A'}")
            print(f"           Rows: {v.row_count}, Fetched: {v.fetched_at}")
    print()


def print_redirects(registry: Registry):
    """Print all URL redirects"""
    redirects = registry.list_redirects()
    if not redirects:
        print("\nNo redirects configured.\n")
        return

    print(f"\nURL Redirects ({len(redirects)}):\n")
    for r in redirects:
        target = r.target_url or f"→ {r.target_dataset_id}"
        print(f"  /{r.old_slug}  {target}")
        if r.reason:
            print(f"      Reason: {r.reason}")
        print(f"      Created: {r.created_at}, Hits: {r.hit_count}")
        print()


def print_published(registry: Registry):
    """Print all published datasets"""
    datasets = registry.get_published_datasets()
    if not datasets:
        print("\nNo published datasets.\n")
        return

    print(f"\nPublished Datasets ({len(datasets)}):\n")
    for d in datasets:
        status = "⚠️ DEPRECATED" if d.deprecated_at else "✅ Active"
        print(f"  /{d.canonical_slug}")
        print(f"      Dataset: {d.id}")
        print(f"      Title: {d.name_en}")
        print(f"      Published: {d.first_published_at}, Status: {status}")
        if d.deprecated_at:
            print(f"      Deprecated: {d.deprecated_at}")
            if d.successor_id:
                print(f"      Successor: {d.successor_id}")
        print()


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Data.mn Registry Management')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Status command
    subparsers.add_parser('status', help='Show registry status')

    # Sources command
    subparsers.add_parser('sources', help='List all sources')

    # List command
    list_parser = subparsers.add_parser('list', help='List datasets')
    list_parser.add_argument('--source', help='Filter by source ID')
    list_parser.add_argument('--status', help='Filter by status')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show dataset details')
    info_parser.add_argument('dataset_id', help='Dataset ID')

    # URL Stability commands
    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish a dataset (assign canonical URL)')
    publish_parser.add_argument('dataset_id', help='Dataset ID to publish')
    publish_parser.add_argument('--slug', help='Custom URL slug (defaults to dataset_id)')

    # Rename command
    rename_parser = subparsers.add_parser('rename', help='Rename a URL slug (creates redirect)')
    rename_parser.add_argument('dataset_id', help='Dataset ID to rename')
    rename_parser.add_argument('new_slug', help='New URL slug')
    rename_parser.add_argument('--reason', required=True, help='Reason for rename (required)')

    # Deprecate command
    deprecate_parser = subparsers.add_parser('deprecate', help='Mark a dataset as deprecated')
    deprecate_parser.add_argument('dataset_id', help='Dataset ID to deprecate')
    deprecate_parser.add_argument('--reason', required=True, help='Reason for deprecation (required)')
    deprecate_parser.add_argument('--successor', help='Successor dataset ID')

    # Add redirect command
    add_redirect_parser = subparsers.add_parser('add-redirect', help='Add a manual URL redirect')
    add_redirect_parser.add_argument('old_slug', help='Old URL slug to redirect from')
    add_redirect_parser.add_argument('--target', help='Target dataset ID')
    add_redirect_parser.add_argument('--url', help='Target URL (for external redirects)')
    add_redirect_parser.add_argument('--reason', help='Reason for redirect')

    # Redirects command
    subparsers.add_parser('redirects', help='List all URL redirects')

    # Published command
    subparsers.add_parser('published', help='List all published datasets')

    # Export redirects command
    export_parser = subparsers.add_parser('export-redirects', help='Export redirects as JSON for Astro')
    export_parser.add_argument('--output', '-o', help='Output file (defaults to stdout)')

    args = parser.parse_args()
    registry = Registry()

    if args.command == 'status' or args.command is None:
        print_status(registry)
    elif args.command == 'sources':
        print_sources(registry)
    elif args.command == 'list':
        print_datasets(registry, source_id=args.source, status=args.status)
    elif args.command == 'info':
        print_info(registry, args.dataset_id)

    # URL Stability command handlers
    elif args.command == 'publish':
        try:
            result = registry.publish_dataset(args.dataset_id, canonical_slug=args.slug)
            if result:
                slug = args.slug or args.dataset_id
                print(f"✅ Published: /{slug}")
                print(f"   URLs: /en/data/{slug} and /mn/data/{slug}")
            else:
                # Parent dataset - no URL needed
                print(f"⏭️  Skipped: {args.dataset_id} is a parent dataset (no MDX page)")
        except ValueError as e:
            print(f"❌ Error: {e}")

    elif args.command == 'rename':
        try:
            dataset = registry.get_dataset(args.dataset_id)
            old_slug = dataset.canonical_slug if dataset else None
            registry.rename_slug(args.dataset_id, args.new_slug, args.reason)
            print(f"✅ Renamed: /{old_slug} → /{args.new_slug}")
            print(f"   Redirect created from old URL")
        except ValueError as e:
            print(f"❌ Error: {e}")

    elif args.command == 'deprecate':
        try:
            registry.deprecate_dataset(args.dataset_id, args.reason, successor_id=args.successor)
            print(f"✅ Deprecated: {args.dataset_id}")
            print(f"   Reason: {args.reason}")
            if args.successor:
                print(f"   Successor: {args.successor}")
        except ValueError as e:
            print(f"❌ Error: {e}")

    elif args.command == 'add-redirect':
        if not args.target and not args.url:
            print("❌ Error: Must provide --target or --url")
        else:
            try:
                registry.add_redirect(args.old_slug,
                                     target_dataset_id=args.target,
                                     target_url=args.url,
                                     reason=args.reason)
                target = args.url or args.target
                print(f"✅ Redirect added: /{args.old_slug} → {target}")
            except ValueError as e:
                print(f"❌ Error: {e}")

    elif args.command == 'redirects':
        print_redirects(registry)

    elif args.command == 'published':
        print_published(registry)

    elif args.command == 'export-redirects':
        redirects = registry.export_redirects_for_astro()
        output = json.dumps(redirects, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Exported {len(redirects)} redirects to {args.output}")
        else:
            print(output)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
