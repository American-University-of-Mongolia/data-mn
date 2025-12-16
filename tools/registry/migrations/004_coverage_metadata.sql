-- Migration 004: Coverage Metadata and Related Datasets
-- Version: 4 (Coverage Tracking)
--
-- Purpose: Track geographic, temporal, and dimensional coverage of datasets
-- to handle overlapping source tables that cover the same indicator at different
-- granularities (e.g., weekly prices by aimags vs. weekly prices for UB only).
--
-- Key Concepts:
--   - coverage_geography: What regions/areas the data covers
--   - coverage_time_start: When the time series begins
--   - coverage_granularity: Geographic detail level (national, aimag, soum, bag)
--   - coverage_frequency: How often data is updated (weekly, monthly, annual)
--   - related_datasets: Links to other datasets covering the same concept
--   - concept_id: Groups datasets measuring the same thing at different granularities

-- ============================================================================
-- ADD COVERAGE FIELDS TO DATASETS TABLE
-- ============================================================================

-- Geographic coverage: JSON array of region types covered
-- Examples: ["national"], ["Ulaanbaatar"], ["all_aimags"], ["all_aimags", "Ulaanbaatar"]
ALTER TABLE datasets ADD COLUMN coverage_geography TEXT;

-- Geographic granularity level
-- Values: 'national', 'regional', 'aimag', 'soum', 'bag'
-- 'national' = single national value
-- 'regional' = 4-6 regional aggregates (Central, Eastern, Western, Khangai)
-- 'aimag' = 21 provinces + potentially Ulaanbaatar
-- 'soum' = ~330 soums/districts
-- 'bag' = ~1500+ bags/khoroos (lowest level)
ALTER TABLE datasets ADD COLUMN coverage_granularity TEXT;

-- Temporal coverage
ALTER TABLE datasets ADD COLUMN coverage_time_start TEXT;  -- e.g., "2020-01", "1990"
ALTER TABLE datasets ADD COLUMN coverage_time_end TEXT;    -- e.g., "2024-12", NULL for ongoing
ALTER TABLE datasets ADD COLUMN coverage_frequency TEXT;   -- 'weekly', 'monthly', 'quarterly', 'annual'

-- Dimensional coverage (what breakdowns are available)
-- JSON object, e.g., {"sex": true, "age_group": true, "economic_sector": false}
ALTER TABLE datasets ADD COLUMN coverage_dimensions TEXT;

-- Concept linking: groups related datasets measuring the same indicator
-- e.g., 'weekly-prices', 'gdp-per-capita', 'livestock-count', 'unemployment-rate'
ALTER TABLE datasets ADD COLUMN concept_id TEXT;

-- Related datasets: explicit links to alternative datasets for same concept
-- JSON array of dataset IDs, e.g., ["weekly-prices-ulaanbaatar", "monthly-prices-all"]
ALTER TABLE datasets ADD COLUMN related_datasets TEXT;

-- Notes about coverage limitations or special considerations
ALTER TABLE datasets ADD COLUMN coverage_notes TEXT;

-- ============================================================================
-- CONCEPTS TABLE: Defines the statistical concepts that datasets measure
-- ============================================================================

CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,                    -- e.g., 'weekly-prices', 'gdp-per-capita'
    name_en TEXT NOT NULL,                  -- Human-readable name
    name_mn TEXT,                           -- Mongolian name
    description_en TEXT,                    -- What this concept measures
    description_mn TEXT,
    category_en TEXT,                       -- 'Prices', 'Demographics', 'Economy', etc.
    category_mn TEXT,

    -- Best-coverage dataset for this concept (auto-computed or manually set)
    -- This is the "recommended" dataset when users search for this concept
    primary_dataset_id TEXT REFERENCES datasets(id),

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_datasets_concept ON datasets(concept_id);
CREATE INDEX IF NOT EXISTS idx_datasets_coverage_granularity ON datasets(coverage_granularity);
CREATE INDEX IF NOT EXISTS idx_datasets_coverage_frequency ON datasets(coverage_frequency);

-- ============================================================================
-- UPDATE SCHEMA VERSION
-- ============================================================================

INSERT INTO schema_version (version, applied_at, description)
VALUES (4, datetime('now'), 'Coverage metadata and related datasets');
