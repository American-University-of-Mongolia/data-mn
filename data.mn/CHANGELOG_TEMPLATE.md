# Changelog Entry Template

This template provides instructions for creating changelog entries to track dataset additions, updates, and removals on Data.mn.

## Overview

Changelog entries are MDX files that document changes to the dataset collection. They are displayed on the `/changelog` page in both English and Mongolian.

## File Naming Convention

Files should be named using the following pattern:

```
{YYYY-MM-DD}-{dataset-id}.mdx
```

Examples:
- `2025-12-05-population-total.mdx`
- `2025-12-01-gdp-quarterly.mdx`
- `2025-11-28-mining-permits.mdx`

## Directory Structure

- **English entries**: `src/data/changelog/en/`
- **Mongolian entries**: `src/data/changelog/mn/`

**IMPORTANT**: Both English and Mongolian versions must be created for each changelog entry.

## Required Fields

All changelog entries must include the following frontmatter fields:

```yaml
---
date: 2025-12-05  # Date of the change (YYYY-MM-DD format)
action: added     # One of: added, updated, removed
dataset_id: population-total  # The dataset's ID (slug)
dataset_name_en: Mongolia Total Population (1956-2024)  # English dataset name
dataset_name_mn: Монгол Улсын нийт хүн ам (1956-2024)  # Mongolian dataset name
description_en: Initial release of historical population data from NSO 1212.mn  # English description
description_mn: ҮСХ 1212.mn-ээс авсан түүхэн хүн амын өгөгдлийн анхны хувилбар  # Mongolian description
source: National Statistics Office  # Optional: data source name
version: 1  # Optional: version number
---
```

## Action Types

Use the appropriate action type for your changelog entry:

- **`added`**: New dataset added to the collection
- **`updated`**: Existing dataset updated with new data or improvements
- **removed`**: Dataset removed or deprecated (use sparingly)

## Template for English Entry

File: `src/data/changelog/en/{YYYY-MM-DD}-{dataset-id}.mdx`

```mdx
---
date: 2025-12-05
action: added
dataset_id: population-total
dataset_name_en: Mongolia Total Population (1956-2024)
dataset_name_mn: Монгол Улсын нийт хүн ам (1956-2024)
description_en: Initial release of historical population data from NSO 1212.mn covering 1956 to 2024. Includes annual population totals with interactive time series visualization.
description_mn: ҮСХ 1212.mn-ээс авсан 1956-2024 оны түүхэн хүн амын өгөгдлийн анхны хувилбар. Жилийн нийт хүн амын тоо, интерактив цаг хугацааны дүрслэл орсон.
source: National Statistics Office
version: 1
---
```

## Template for Mongolian Entry

File: `src/data/changelog/mn/{YYYY-MM-DD}-{dataset-id}.mdx`

```mdx
---
date: 2025-12-05
action: added
dataset_id: population-total
dataset_name_en: Mongolia Total Population (1956-2024)
dataset_name_mn: Монгол Улсын нийт хүн ам (1956-2024)
description_en: Initial release of historical population data from NSO 1212.mn covering 1956 to 2024. Includes annual population totals with interactive time series visualization.
description_mn: ҮСХ 1212.mn-ээс авсан 1956-2024 оны түүхэн хүн амын өгөгдлийн анхны хувилбар. Жилийн нийт хүн амын тоо, интерактив цаг хугацааны дүрслэл орсон.
source: National Statistics Office
version: 1
---
```

**Note**: The frontmatter is identical in both English and Mongolian files. Both language versions contain both the English and Mongolian text fields.

## Example: Dataset Update

```mdx
---
date: 2025-12-05
action: updated
dataset_id: gdp-quarterly
dataset_name_en: Mongolia Quarterly GDP (2000-2024)
dataset_name_mn: Монгол Улсын улирлын ДНБ (2000-2024)
description_en: Updated with Q3 2024 data from Bank of Mongolia. Added year-over-year growth rate calculations.
description_mn: Монголбанкнаас авсан 2024 оны 3-р улирлын өгөгдлөөр шинэчлэв. Өмнөх оны мөн үеэс өссөн хурдыг нэмж тооцоолов.
source: Bank of Mongolia
version: 5
---
```

## Example: Dataset Removal

```mdx
---
date: 2025-12-05
action: removed
dataset_id: old-salary-data
dataset_name_en: Average Salary by Sector (2010-2020)
dataset_name_mn: Салбараар дундаж цалин (2010-2020)
description_en: Deprecated in favor of the new comprehensive salary dataset with extended time range and additional breakdowns.
description_mn: Сунгасан хугацаа болон нэмэлт ангиллаар бүрдсэн шинэ иж бүрэн цалингийн өгөгдлөөр солигдсон.
source: National Statistics Office
---
```

## Writing Descriptions

### Good Descriptions

- Clear and concise (1-2 sentences)
- Specify what's new or changed
- Mention the data source
- Include time range or key metrics
- Note any special features (charts, breakdowns, etc.)

### Examples

**For "added" actions:**
- "Initial release of monthly inflation data from NSO 1212.mn covering January 2000 to November 2024."
- "New dataset tracking mining permits by region and mineral type, sourced from MRPAM monthly reports."

**For "updated" actions:**
- "Updated with November 2024 data from NSO. Added seasonal adjustment calculations."
- "Refreshed with Q4 2024 data. Extended historical coverage back to 1990."

**For "removed" actions:**
- "Deprecated and replaced by the consolidated trade statistics dataset."
- "Removed due to data quality issues. Will be re-added when source data is corrected."

## Checklist Before Creating Changelog Entry

- [ ] Dataset is published and accessible at `/{lang}/data/{dataset-id}`
- [ ] Both English and Mongolian MDX files are created
- [ ] File names follow the `{YYYY-MM-DD}-{dataset-id}.mdx` pattern
- [ ] All required frontmatter fields are filled in
- [ ] Date is in YYYY-MM-DD format
- [ ] Action is one of: added, updated, removed
- [ ] Dataset names match the actual dataset titles
- [ ] Descriptions are clear and informative in both languages
- [ ] Files are saved in correct directories (`en/` and `mn/`)

## Tips

1. **Keep it factual**: Focus on what changed, not why it's important
2. **Be specific**: Include version numbers, date ranges, or data counts when relevant
3. **Maintain consistency**: Use similar language patterns for similar changes
4. **Update regularly**: Create changelog entries whenever datasets are added or updated
5. **Don't backfill**: Only track changes going forward from the date this system is implemented

## Questions?

If you have questions about creating changelog entries, refer to:
- The Data.mn CLAUDE.md file
- The `/data-add` and `/data-update` slash command documentation
- Existing changelog entries in `src/data/changelog/en/` and `mn/` for examples
