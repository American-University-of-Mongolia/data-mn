# URL Stability Principles

> "Cool URIs don't change" — Tim Berners-Lee, 1998

This document defines the principles and rules for maintaining stable, permanent URLs on data.mn. These principles are critical for a data platform where URLs will be cited in academic papers, government reports, and linked from external systems.

## Why URL Stability Matters

### 1. Citation Permanence
Researchers, journalists, and analysts will cite data.mn URLs in their work. A broken URL invalidates citations and damages trust.

### 2. SEO Value Accumulation
URLs accumulate search engine authority over time. A 3-year-old URL with backlinks is far more valuable than a new one.

### 3. API Consumer Trust
Scripts, dashboards, and external systems may hardcode URLs. Breaking them causes cascading failures.

### 4. Data Versioning ≠ URL Versioning
The data at a URL should update, but the URL itself should remain constant. Version 1 and Version 50 of "Total Population" live at the same URL.

---

## Core Principles

### Principle 1: URLs Are Forever
Once a URL is published, it must work indefinitely. There are no exceptions.

### Principle 2: Rename via Redirect, Never Replace
If a URL must change, the old URL redirects (301) to the new one. Both URLs work forever.

### Principle 3: Deprecate, Don't Delete
Obsolete data is marked deprecated, not removed. The URL continues to work with a deprecation notice.

### Principle 4: Canonical Slugs Are Immutable
The `canonical_slug` assigned at first publication is permanent. It's like a database primary key.

### Principle 5: First Published Date Is Sacred
`first_published_at` marks when a URL went live. This date never changes, even if the data is updated.

---

## URL Lifecycle States

```
┌──────────┐   ┌───────────┐   ┌────────────┐   ┌─────────────┐
│  DRAFT   │──►│ PUBLISHED │──►│ DEPRECATED │──►│  REDIRECTED │
│          │   │           │   │            │   │             │
│ No URL   │   │ URL live  │   │ URL works  │   │ URL works   │
│ assigned │   │ canonical │   │ with notice│   │ → successor │
└──────────┘   └───────────┘   └────────────┘   └─────────────┘
                     │
                     │ rename needed
                     ▼
               ┌───────────┐
               │  ALIASED  │
               │           │
               │ Old URL   │
               │ redirects │
               │ to new    │
               └───────────┘
```

### State Definitions

| State | URL Works? | Data Accessible? | Notes |
|-------|------------|------------------|-------|
| **DRAFT** | N/A | No | Not yet published, no URL assigned |
| **PUBLISHED** | ✅ Yes | Yes | Active dataset with stable URL |
| **DEPRECATED** | ✅ Yes | Yes (with notice) | Data obsolete but URL works |
| **REDIRECTED** | ✅ Yes (301) | Via redirect | Old URL forwards to successor |
| **ALIASED** | ✅ Yes (301) | Via redirect | URL renamed, old URL forwards |

---

## Operations and Rules

### Publishing a Dataset
```bash
python -m registry publish <dataset_id> [--slug <custom-slug>]
```

Rules:
- Assigns `canonical_slug` (defaults to `id` if not specified)
- Sets `first_published_at` to current timestamp
- Sets `is_published = 1`
- **Cannot be undone** — once published, the slug is permanent

### Renaming a URL
```bash
python -m registry rename <dataset_id> <new-slug> --reason "..."
```

Rules:
- Creates redirect from old slug to new slug
- Updates `canonical_slug` to new value
- Both URLs work forever
- Reason is required for audit trail

Example:
```bash
# Rename from population-total to population-total-mongolia
python -m registry rename population-total population-total-mongolia \
  --reason "Added country suffix for consistency"
```

After this:
- `/en/data/population-total` → 301 → `/en/data/population-total-mongolia`
- `/en/data/population-total-mongolia` → works directly

### Deprecating a Dataset
```bash
python -m registry deprecate <dataset_id> --reason "..." [--successor <id>]
```

Rules:
- Sets `deprecated_at` timestamp
- Sets `deprecation_reason`
- Optionally links to `successor_id`
- **URL continues to work** with deprecation notice
- Data remains accessible

Example:
```bash
# Deprecate old GDP dataset, point to new one
python -m registry deprecate gdp-old \
  --reason "Methodology changed in 2024" \
  --successor gdp-by-activity
```

### Adding Manual Redirects
```bash
python -m registry add-redirect <old-slug> --target <dataset-id> --reason "..."
```

Rules:
- For redirects not from renames (e.g., fixing typos, consolidation)
- Creates 301 redirect
- Reason required for audit

---

## Database Schema

### Datasets Table (URL-related columns)
```sql
canonical_slug TEXT,           -- Permanent URL slug (immutable after publish)
first_published_at TEXT,       -- When URL first went live
is_published INTEGER DEFAULT 0, -- Whether currently published
deprecated_at TEXT,            -- When marked deprecated (NULL if active)
deprecation_reason TEXT,       -- Why deprecated
successor_id TEXT              -- Replacement dataset if deprecated
```

### URL Redirects Table
```sql
CREATE TABLE url_redirects (
    id INTEGER PRIMARY KEY,
    old_slug TEXT NOT NULL UNIQUE,  -- Slug being redirected FROM
    target_dataset_id TEXT,         -- Dataset redirecting TO
    target_url TEXT,                -- Or full URL if external
    redirect_type INTEGER DEFAULT 301,
    reason TEXT,                    -- Why redirect exists
    created_at TEXT,
    hit_count INTEGER DEFAULT 0,    -- Analytics
    last_hit_at TEXT
);
```

---

## Implementation Checklist

When creating or updating datasets:

- [ ] **Before first deploy**: Run `python -m registry publish <id>`
- [ ] **Verify slug is permanent**: The `canonical_slug` will live forever
- [ ] **Generate redirects**: Run `python -m registry export-redirects`
- [ ] **Never delete published datasets**: Deprecate instead
- [ ] **Never change canonical_slug directly**: Use `rename` command

---

## Examples

### Good: Renaming with redirect
```bash
# Dataset was published as "pop-total"
# We want cleaner URL "population-total-mongolia"

python -m registry rename pop-total population-total-mongolia \
  --reason "Adopting consistent naming convention"

# Result:
# - /en/data/pop-total → 301 → /en/data/population-total-mongolia
# - Both URLs work forever
```

### Good: Deprecating obsolete data
```bash
# Old methodology population data replaced by new census
python -m registry deprecate population-2020-estimate \
  --reason "2020 census data now available" \
  --successor population-census-2020

# Result:
# - /en/data/population-2020-estimate still works
# - Shows deprecation notice with link to census data
```

### Bad: What NOT to do
```bash
# NEVER do this:
rm src/data/data/en/population-total.mdx  # Deletes published page!
UPDATE datasets SET canonical_slug = 'new-name' WHERE id = 'old-name';  # Breaks old URL!
```

---

## Analytics and Monitoring

The `url_redirects` table tracks:
- `hit_count`: How many times a redirect was used
- `last_hit_at`: When it was last triggered

Use this to:
1. Identify heavily-used legacy URLs
2. Monitor if deprecated datasets still get traffic
3. Detect broken external links (via 404 monitoring)

---

## Related Documents

- `DATA_SYSTEM_PLAN.md` — Overall system architecture
- `CLAUDE.md` — Developer instructions
- `tools/registry/schema.sql` — Database schema

---

## References

- [Cool URIs don't change](https://www.w3.org/Provider/Style/URI) — W3C, Tim Berners-Lee
- [Persistent URLs](https://en.wikipedia.org/wiki/Persistent_uniform_resource_locator) — Wikipedia
- [DOI System](https://www.doi.org/) — Example of permanent identifiers
