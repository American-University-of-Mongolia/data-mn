-- Data.mn Registry Schema
-- Version: 3 (URL Stability)

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);

-- Insert current schema version
INSERT INTO schema_version (version, applied_at, description)
VALUES (1, datetime('now'), 'Initial schema');

-- Data sources (where data comes from)
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,                    -- e.g., 'nso-1212', 'mrpam', 'mongolbank'
    name TEXT NOT NULL,                     -- Human-readable name
    name_mn TEXT,                           -- Mongolian name
    type TEXT NOT NULL,                     -- 'api', 'pdf', 'scrape', 'manual'
    base_url TEXT,                          -- Base URL for the source
    definition_path TEXT NOT NULL,          -- Path to source.md: 'sources/nso-1212/source.md'
    update_frequency TEXT DEFAULT 'unknown', -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    enabled INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 50,            -- Lower = higher priority for updates
    config TEXT,                            -- JSON: Source-specific config
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Individual datasets
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,                    -- Unique ID: 'nso-population-total'
    source_id TEXT NOT NULL REFERENCES sources(id),

    -- Parent/Split relationship
    parent_id TEXT REFERENCES datasets(id), -- If this is a split, references the parent dataset
    is_parent INTEGER DEFAULT 0,            -- 1 if this dataset has splits defined
    split_filter TEXT,                      -- JSON: Filter criteria for this split (e.g., {"sex": "Total", "age_group": "Total"})

    -- Metadata
    name_en TEXT NOT NULL,
    name_mn TEXT,
    description_en TEXT,
    description_mn TEXT,
    category_en TEXT NOT NULL,              -- 'Demographics', 'Economy', etc.
    category_mn TEXT,                       -- 'Хүн ам зүй', 'Эдийн засаг', etc.
    tags TEXT,                              -- JSON array of tags
    keywords_en TEXT,                       -- JSON: Search keywords (English)
    keywords_mn TEXT,                       -- JSON: Search keywords (Mongolian)

    -- Source-specific reference
    source_ref TEXT,                        -- e.g., 1212 table ID: 'DT_NSO_0300_001V2.px'
    source_path TEXT,                       -- API path or URL
    definition_path TEXT NOT NULL,          -- Path to dataset definition
    source_metadata TEXT,                   -- JSON: Full source metadata

    -- Current state
    current_version INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',          -- 'pending', 'active', 'outdated', 'error', 'disabled'

    -- Files
    data_file TEXT,                         -- Relative path to current CSV
    mdx_file_en TEXT,                       -- Path to English MDX
    mdx_file_mn TEXT,                       -- Path to Mongolian MDX
    chart_spec TEXT,                        -- Path to Vega-Lite spec

    -- Timing
    data_as_of TEXT,                        -- When the data itself is from
    source_updated_at TEXT,                 -- When source last updated
    last_checked_at TEXT,                   -- When we last checked source
    last_fetched_at TEXT,                   -- When we last fetched data

    -- Auto-generation settings
    auto_update INTEGER DEFAULT 1,          -- Auto-fetch when source updates
    auto_publish INTEGER DEFAULT 1,         -- Auto-regenerate MDX

    -- URL Stability (see docs/principles/url-stability.md)
    canonical_slug TEXT,                    -- Permanent URL slug (immutable after first publish)
    first_published_at TEXT,                -- When URL first went live (NULL if unpublished)
    is_published INTEGER DEFAULT 0,         -- Whether currently published on site
    deprecated_at TEXT,                     -- When marked deprecated (NULL if active)
    deprecation_reason TEXT,                -- Why deprecated (human-readable)
    successor_id TEXT REFERENCES datasets(id), -- Replacement dataset if deprecated

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Version history (full history)
CREATE TABLE IF NOT EXISTS versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_id TEXT NOT NULL REFERENCES datasets(id),
    version INTEGER NOT NULL,

    -- Version data
    data_hash TEXT NOT NULL,                -- SHA256 of data file
    data_path TEXT NOT NULL,                -- Path in versions/{dataset_id}/v{version}/
    row_count INTEGER,
    column_count INTEGER,

    -- Changes
    change_type TEXT,                       -- 'initial', 'update', 'correction', 'schema_change'
    change_summary TEXT,                    -- Human-readable changes
    diff_stats TEXT,                        -- JSON: {rows_added: N, rows_removed: N, rows_modified: N}

    -- Source info
    source_updated_at TEXT,
    source_raw_files TEXT,                  -- JSON: List of raw source files archived

    fetched_at TEXT DEFAULT (datetime('now')),

    UNIQUE(dataset_id, version)
);

-- Activity log
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),

    -- What
    action TEXT NOT NULL,                   -- 'check', 'fetch', 'update', 'publish', 'error'
    dataset_id TEXT REFERENCES datasets(id),
    source_id TEXT REFERENCES sources(id),

    -- Details
    status TEXT,                            -- 'success', 'no_update', 'error'
    message TEXT,
    details TEXT,                           -- JSON

    -- Who (for audit)
    triggered_by TEXT DEFAULT 'manual'      -- 'manual', 'scheduled', 'command'
);

-- URL Redirects (for URL stability)
-- See docs/principles/url-stability.md for full documentation
CREATE TABLE IF NOT EXISTS url_redirects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    old_slug TEXT NOT NULL UNIQUE,          -- URL slug being redirected FROM
    target_dataset_id TEXT REFERENCES datasets(id), -- Dataset redirecting TO (NULL if external)
    target_url TEXT,                        -- Full URL if redirecting externally
    redirect_type INTEGER DEFAULT 301,      -- 301 (permanent) or 302 (temporary)
    reason TEXT,                            -- Why this redirect exists (audit trail)
    created_at TEXT DEFAULT (datetime('now')),
    hit_count INTEGER DEFAULT 0,            -- How many times redirect was used
    last_hit_at TEXT                        -- When redirect was last triggered
);

-- NSO 1212 metadata cache (for searching available tables)
CREATE TABLE IF NOT EXISTS nso_sectors (
    id TEXT PRIMARY KEY,
    name_en TEXT,
    name_mn TEXT,
    type TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS nso_subsectors (
    id TEXT,
    sector_id TEXT,
    name_en TEXT,
    name_mn TEXT,
    type TEXT,
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (sector_id, id),
    FOREIGN KEY (sector_id) REFERENCES nso_sectors(id)
);

CREATE TABLE IF NOT EXISTS nso_tables (
    id TEXT,
    subsector_id TEXT,
    sector_id TEXT,
    name_en TEXT,
    name_mn TEXT,
    type TEXT,
    last_updated TEXT,
    keywords TEXT,
    full_path TEXT,
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (sector_id, subsector_id, id)
);

-- Full-text search for NSO tables
CREATE VIRTUAL TABLE IF NOT EXISTS nso_tables_fts USING fts5(
    id,
    name_en,
    name_mn,
    keywords,
    full_path,
    content=nso_tables,
    content_rowid=rowid
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_datasets_source ON datasets(source_id);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON datasets(status);
CREATE INDEX IF NOT EXISTS idx_datasets_category ON datasets(category_en);
CREATE INDEX IF NOT EXISTS idx_datasets_parent ON datasets(parent_id);
CREATE INDEX IF NOT EXISTS idx_versions_dataset ON versions(dataset_id);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_dataset ON activity_log(dataset_id);
CREATE INDEX IF NOT EXISTS idx_datasets_canonical_slug ON datasets(canonical_slug);
CREATE INDEX IF NOT EXISTS idx_datasets_published ON datasets(is_published);
CREATE INDEX IF NOT EXISTS idx_redirects_old_slug ON url_redirects(old_slug);

-- Triggers to update timestamps
CREATE TRIGGER IF NOT EXISTS update_sources_timestamp
AFTER UPDATE ON sources
BEGIN
    UPDATE sources SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_datasets_timestamp
AFTER UPDATE ON datasets
BEGIN
    UPDATE datasets SET updated_at = datetime('now') WHERE id = NEW.id;
END;
