# Coverage Detection and Related Datasets

This document describes how to detect, document, and handle **overlapping datasets** - source tables that measure the same indicator at different geographic, temporal, or dimensional granularities.

## The Problem

Data sources like NSO 1212.mn often publish the same statistical indicator in multiple tables with different coverage:

| Table | Indicator | Geographic | Temporal | History |
|-------|-----------|------------|----------|---------|
| `0600_001V4` | Weekly Prices | Ulaanbaatar only | Weekly | 5 years |
| `0300_010V5` | Weekly Prices | 21 aimags (no UB) | Weekly | 2 years |
| `0600_019V1` | Monthly Prices | All (aimags + UB) | Monthly | 10+ years |

Without tracking this, we risk:
- Adding datasets that duplicate existing data
- Confusing users about which dataset to use
- Missing better coverage options

## The Solution: Coverage Metadata

Every dataset must document its coverage across these dimensions:

### 1. Geographic Coverage (`coverage_geography`)

JSON array of region types covered:

```json
["Ulaanbaatar"]                    // UB only
["all_aimags"]                     // 21 provinces, no UB
["all_aimags", "Ulaanbaatar"]      // Complete national coverage
["national"]                        // Single national aggregate
["regional_aggregates"]            // 4-6 regions (Central, Eastern, Western, Khangai)
```

### 2. Geographic Granularity (`coverage_granularity`)

How detailed is the geographic breakdown?

| Value | Description | Typical Count |
|-------|-------------|---------------|
| `national` | Single national value | 1 |
| `regional` | Regional aggregates | 4-6 |
| `aimag` | Provinces + Capital | 21-22 |
| `soum` | Districts/soums | ~330 |
| `bag` | Lowest admin level | ~1,500+ |

### 3. Temporal Coverage

- `coverage_time_start`: When data begins (e.g., "2020-01", "1990")
- `coverage_time_end`: When data ends (NULL for ongoing)
- `coverage_frequency`: Update frequency ("weekly", "monthly", "quarterly", "annual")

### 4. Dimensional Coverage (`coverage_dimensions`)

JSON object of available breakdowns:

```json
{
    "sex": true,
    "age_group": true,
    "economic_sector": false,
    "urban_rural": true
}
```

### 5. Concept ID (`concept_id`)

Groups datasets measuring the same thing:

```
concept_id: "weekly-prices"
├── weekly-prices-ulaanbaatar     (UB only, 5 years)
├── weekly-prices-aimags          (provinces, 2 years)
└── monthly-prices-all            (complete, monthly)
```

### 6. Related Datasets (`related_datasets`)

JSON array of alternative dataset IDs:

```json
["weekly-prices-ulaanbaatar", "monthly-prices-all"]
```

---

## Coverage Detection Process

### When Adding a New Dataset

**Before creating a new dataset**, always run coverage detection:

#### Step 1: Search for Related Tables

```bash
# Search for similar tables in NSO
cd .claude/skills/datamn-source-nso
python3 query_api.py "weekly prices"
```

#### Step 2: Identify Coverage Pattern

Look for tables with similar names but different suffixes:
- "by aimags" vs "by aimags and the Capital"
- "by soum" vs "by aimag"
- "monthly" vs "weekly" vs "annual"

#### Step 3: Check Existing Registry

```bash
cd data/tools
python -m registry list | grep -i "price"
```

#### Step 4: Document Coverage Differences

For each related table, document:

| Field | Table A | Table B |
|-------|---------|---------|
| Geographic coverage | UB only | All aimags (no UB) |
| Granularity | - | aimag |
| Time start | 2020-01 | 2024-01 |
| Frequency | weekly | weekly |
| Products | 31 | 11 |

#### Step 5: Decision Matrix

| Scenario | Action |
|----------|--------|
| New coverage not in registry | Add as new dataset with coverage metadata |
| Better coverage exists | Consider updating existing or adding as related |
| Same coverage, different products | Add as separate dataset |
| Subset of existing | Link as related, may skip adding |

---

## Naming Conventions

When coverage varies, encode it in the dataset ID:

### Geographic Qualifiers

```
weekly-prices-ulaanbaatar    # UB only
weekly-prices-aimags         # Provinces only, no UB
weekly-prices-national       # Single national value
livestock-by-soum            # Soum-level detail
```

### Temporal Qualifiers

```
gdp-quarterly                # Quarterly data
gdp-annual                   # Annual data
prices-monthly               # Monthly frequency
```

### Do NOT add qualifiers when:
- There's only one source table (no alternatives)
- The dataset has complete coverage (aimags + UB)
- The qualifier would be redundant

---

## Registry Commands

### Add Coverage to Existing Dataset

```python
from registry import Registry

reg = Registry()
reg.update_dataset(
    dataset_id='weekly-beef-prices',
    coverage_geography='["all_aimags", "regional_aggregates"]',
    coverage_granularity='aimag',
    coverage_time_start='2024-01',
    coverage_frequency='weekly',
    concept_id='weekly-prices',
    related_datasets='["weekly-prices-ulaanbaatar"]'
)
```

### Create a Concept

```python
reg.add_concept(
    concept_id='weekly-prices',
    name_en='Weekly Prices of Main Products',
    name_mn='Үндсэн бүтээгдэхүүний долоо хоногийн үнэ',
    description_en='Weekly price monitoring of essential goods',
    category_en='Prices',
    primary_dataset_id='weekly-prices-aimags'  # Best coverage option
)
```

### Find Related Datasets

```python
related = reg.get_datasets_by_concept('weekly-prices')
for ds in related:
    print(f"{ds.id}: {ds.coverage_geography} ({ds.coverage_frequency})")
```

---

## Agent Workflow

When a data agent (datamn-dataset-worker) adds a new dataset:

### 1. Coverage Check Phase

```
Before creating dataset definition:
1. Search NSO for similar table names
2. Query registry for same concept_id
3. If related tables found:
   a. Compare coverage (geography, time, frequency)
   b. Determine if this adds value or duplicates
   c. Assign appropriate qualified name
   d. Link as related_datasets
```

### 2. Documentation Phase

```
In dataset definition markdown:
1. Add "## Coverage" section documenting:
   - Geographic: What regions are included
   - Temporal: Time range and frequency
   - Limitations: What's missing (e.g., "No Ulaanbaatar data")
2. Add "## Related Tables" section listing alternatives
```

### 3. Registration Phase

```
When registering in database:
1. Set all coverage_* fields
2. Set concept_id (create concept if new)
3. Set related_datasets array
4. Update related datasets to include this one
```

---

## Examples

### Example 1: Weekly Prices

```yaml
# weekly-prices-aimags
concept_id: weekly-prices
coverage_geography: ["all_aimags", "regional_aggregates"]
coverage_granularity: aimag
coverage_time_start: "2024-01"
coverage_frequency: weekly
related_datasets: ["weekly-prices-ulaanbaatar"]
coverage_notes: "Does not include Ulaanbaatar. For UB data, see weekly-prices-ulaanbaatar."

# weekly-prices-ulaanbaatar
concept_id: weekly-prices
coverage_geography: ["Ulaanbaatar"]
coverage_granularity: null  # No geographic breakdown within UB
coverage_time_start: "2020-01"
coverage_frequency: weekly
related_datasets: ["weekly-prices-aimags"]
coverage_notes: "Ulaanbaatar/national prices only. More products (31) and longer history than aimag data."
```

### Example 2: GDP Per Capita

```yaml
# gdp-per-capita-national
concept_id: gdp-per-capita
coverage_geography: ["national"]
coverage_granularity: national
coverage_time_start: "1990"
coverage_frequency: annual
related_datasets: ["gdp-per-capita-aimags"]
coverage_notes: "35+ years of history. For regional breakdown, see gdp-per-capita-aimags."

# gdp-per-capita-aimags
concept_id: gdp-per-capita
coverage_geography: ["all_aimags", "Ulaanbaatar", "regional_aggregates"]
coverage_granularity: aimag
coverage_time_start: "2009"
coverage_frequency: annual
related_datasets: ["gdp-per-capita-national"]
coverage_notes: "Regional breakdown available. Shorter history than national dataset."
```

---

## UI/UX Implications

On dataset pages, show:

1. **Coverage Summary Box**:
   ```
   Coverage: 21 aimags + 4 regional aggregates
   Frequency: Weekly
   Time Range: Jan 2024 - Present
   Note: Ulaanbaatar not included
   ```

2. **Related Data Section**:
   ```
   Related Datasets:
   - Weekly Prices (Ulaanbaatar) - UB prices, longer history
   - Monthly Prices (All Regions) - Less frequent but complete coverage
   ```

---

## Summary

1. **Always search for related tables** before adding a new dataset
2. **Document coverage explicitly** using the coverage_* fields
3. **Name datasets to show scope** when alternatives exist
4. **Link related datasets** bidirectionally
5. **Use concept_id** to group datasets measuring the same thing
6. **Add coverage notes** explaining limitations and alternatives
