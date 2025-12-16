# Category System

This document describes the canonical category system for data.mn datasets.

## Overview

Categories provide high-level organization for datasets, helping users navigate and discover related data. Each dataset must belong to exactly one category, using the **canonical** category name defined in `tools/config/categories.json`.

## Canonical Categories

| ID | English | Mongolian | Description |
|----|---------|-----------|-------------|
| `economy` | Economy | Эдийн засаг | GDP, national accounts, economic growth |
| `prices` | Prices & Inflation | Үнэ ба инфляци | Consumer prices, inflation rates, commodity prices |
| `labor-market` | Labor Market | Хөдөлмөрийн зах зээл | Employment, unemployment, wages, labor force |
| `trade` | Trade | Худалдаа | Imports, exports, trade balance |
| `finance` | Finance | Санхүү | Banking, FDI, foreign reserves, remittances |
| `demographics` | Demographics | Хүн ам зүй | Population, age distribution, migration |
| `household` | Household & Income | Өрх ба орлого | Household income, expenditure, poverty |
| `agriculture` | Agriculture | Хөдөө аж ахуй | Livestock, crops, farming |
| `mining` | Mining & Resources | Уул уурхай | Coal, copper, gold, minerals |
| `education` | Education | Боловсрол | Schools, enrollment, literacy |
| `health` | Health | Эрүүл мэнд | Healthcare, disease, mortality |
| `infrastructure` | Infrastructure | Дэд бүтэц | Housing, transport, energy, telecoms |

## Design Principles

### 1. User-Centric Organization

Categories are designed for **general audiences**, not statisticians. They reflect how people typically think about data topics:

- ✅ "Prices & Inflation" - immediately clear what you'll find
- ❌ "Consumer Price Index" - too technical

### 2. Balanced Distribution

Categories should have roughly similar numbers of datasets. Avoid catch-all categories:

- ❌ **Old**: "Economy" had 60+ datasets (GDP, inflation, unemployment, trade, prices, salaries, etc.)
- ✅ **New**: Split into focused categories (Economy, Prices, Labor Market, Trade, Finance, Household)

### 3. Future-Proof

Categories are chosen to accommodate anticipated data sources:

- `mining` - Reserved for MRPAM mining statistics
- `education` / `health` - Reserved for future NSO/ministry data
- `infrastructure` - Combines Housing, Transport, Energy (avoids small categories)

## Using Categories in MDX Pages

### Frontmatter Format

English pages use English category names:
```yaml
---
category: "Labor Market"
---
```

Mongolian pages use Mongolian category names:
```yaml
---
category: "Хөдөлмөрийн зах зээл"
---
```

### Category Pairing Rules

Each category has a fixed English-Mongolian pair. **Never mix them**:

| English Page Uses | Mongolian Page Uses |
|-------------------|---------------------|
| `"Economy"` | `"Эдийн засаг"` |
| `"Labor Market"` | `"Хөдөлмөрийн зах зээл"` |
| `"Prices & Inflation"` | `"Үнэ ба инфляци"` |
| ... | ... |

## Aliases (Backward Compatibility)

The `categories.json` file includes an `aliases` section mapping old category names to canonical IDs. This helps:

1. **Validation scripts** identify pages using old names
2. **Migration** from old names to canonical names
3. **Documentation** of deprecated naming conventions

Example aliases:
```json
{
  "aliases": {
    "en": {
      "Labour & Employment": "labor-market",
      "Labour Market": "labor-market",
      "Inflation": "prices"
    },
    "mn": {
      "Хөдөлмөр ба Ажлын байр": "labor-market"
    }
  }
}
```

**Important**: Aliases exist for documentation only. Always use canonical names in MDX pages.

## Comparison with NSO 1212.mn

The NSO API uses 8 broad sectors designed for government reporting:

| NSO Sector | data.mn Mapping |
|------------|-----------------|
| Economy, environment | Economy, Prices, Trade, Finance |
| Education, health | Education, Health |
| Industry, service | Agriculture, Mining, Infrastructure |
| Labour, business | Labor Market |
| Population, household | Demographics, Household |
| Regional development | (Data distributed across categories) |
| Society, development | (Household, Demographics) |
| Historical data | (Data distributed across categories) |

We deliberately use more focused categories than NSO because:
1. Users browse by topic, not administrative classification
2. Smaller categories improve discoverability
3. Clear categories help with future data addition decisions

## Adding New Categories

Before adding a new category, consider:

1. **Does existing category fit?** Can the data go in a current category?
2. **Will it have 5+ datasets?** Avoid categories with only 1-2 datasets
3. **Is it user-intuitive?** Would someone searching for this data think to look there?

To add a new category:

1. Edit `tools/config/categories.json`
2. Add entry to `categories` array with `id`, `en`, `mn`, `description`
3. Update this documentation
4. Run validation to ensure no conflicts

## Validation

A validation script checks that all MDX pages use canonical category names:

```bash
cd data/tools
python -m registry validate-categories
```

This reports:
- Pages using alias names (should be updated)
- Pages using unknown categories (typos or missing categories)

## History

- **2025-12-16**: Reorganized from 15 categories to 12. Split "Economy" into focused categories. Fixed alias usage in labor-participation-* pages.
- **2025-12-15**: Initial category system with 15 categories.
