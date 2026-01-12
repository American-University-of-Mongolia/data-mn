---
name: datamn-transform-split
description: Transform and split multi-dimensional datasets into user-friendly filtered views. Use when filtering parent data for splits, generating CSV/XLSX exports, or processing Statista-style dataset splits.
dependencies:
  - python3
  - pandas
  - openpyxl
---

# Data Transformation & Splitting Skill

Transform multi-dimensional source data into user-friendly, single-topic datasets (Statista-style).

## Philosophy

Data from sources like 1212.mn is often highly compressed with multiple dimensions (sex, age, region, year, etc.). This makes it confusing for users.

**Goal**: Split complex datasets into simple datasets that answer ONE clear question each.

### Examples

| Complex (Bad) | Simple (Good) |
|---------------|---------------|
| Population by age, sex, and year | Mongolia Total Population (1956-2024) |
| | Mongolia Population Pyramid (2024) |
| | Mongolia Population by Sex (1956-2024) |

---

## CRITICAL: Files vs Charts Strategy

**Downloadable files should contain ALL data. Charts should show a readable subset.**

This serves two distinct user groups:
1. **Casual users** - Want a clean, readable chart with key insights
2. **Power users** - Want complete data for their own analysis (Excel, Tableau, PowerBI)

### The Three Outputs

| Output | Content | Format | Purpose |
|--------|---------|--------|---------|
| **CSV** | ALL data | Long/tidy form | Technical users, visualization tools (PowerBI, Tableau, R, Python) |
| **XLSX** | ALL data | Wide/pivot form | Excel users, casual data exploration |
| **Chart** | SUBSET | Visual | Immediate insight, must be readable (4-6 categories max) |

### Long vs Wide Format

**Long/Tidy Format (CSV)** - One observation per row:
```csv
date,region,price
2024-01-02,Darkhan-Uul,13000
2024-01-02,Ulaanbaatar,12500
2024-01-02,Khovd,14000
```

**Wide/Pivot Format (XLSX)** - Categories as columns:
```
date        | Darkhan-Uul | Ulaanbaatar | Khovd  | ...
2024-01-02  | 13000       | 12500       | 14000  | ...
2024-01-08  | 13500       | 12800       | 14200  | ...
```

### Chart Subset Selection

When data has many categories (>6 regions, products, etc.), select a **representative subset** for the chart:

1. **Include geographic diversity** - Different parts of the country
2. **Include variety** - Mix of high/low values if applicable
3. **Prefer recognizable names** - Major cities, well-known regions
4. **Maximum 4-6 categories** - More becomes unreadable

**Example for regional price data:**
- Chart shows: Ulaanbaatar, Darkhan-Uul, Khovd, Umnugovi (4 regions)
- Files contain: All 21 aimags + 4 regional aggregates (25 regions)

### Split Config with Chart Subset

```python
split_config = {
    "id": "weekly-beef-prices",
    "parent_id": "nso-weekly-prices-main-products",
    "title_en": "Weekly Beef Prices by Region in Mongolia",
    "filter": {"product": "Beef, kg"},
    # NEW: chart_subset defines what appears in the visualization
    "chart_subset": {
        "column": "region",
        "values": ["Ulaanbaatar", "Darkhan-Uul", "Khovd", "Umnugovi"]
    }
}
```

The `chart_subset` is used when generating the chart JSON and chart-specific CSV, but the full downloadable files ignore it.

## Parent/Split Architecture

### Parent Dataset
- Contains the complete raw multi-dimensional data
- Registered with `is_parent=1` in the registry
- Stored in `data/tools/versions/{parent-id}/`
- Has a `## Splits` section defining child datasets

### Split Dataset
- Filtered view of parent data
- Registered with `parent_id` pointing to parent
- Has `split_filter` JSON defining filter criteria
- Gets its own CSV, XLSX, chart, and MDX pages

## Split Filter Format

Filters are JSON objects specifying which rows to keep:

```json
{
  "sex": "Total",
  "age_group": "Total"
}
```

### Special Values

| Value | Meaning |
|-------|---------|
| `"Total"` | Keep only rows where column equals "Total" |
| `"latest"` | Keep only the most recent year |
| `"NOT X"` | Keep rows where column does NOT equal X |
| `["A", "B"]` | Keep rows where column is A or B |

### Examples

**Total Population Over Time:**
```json
{"sex": "Total", "age_group": "Total"}
```

**Population Pyramid (Latest Year):**
```json
{"year": "latest", "sex": "NOT Total", "age_group": "NOT Total"}
```

**Population by Sex (Excluding Total):**
```json
{"age_group": "Total", "sex": "NOT Total"}
```

## Transformation Workflow

### 1. Load Parent Data

```python
import pandas as pd

parent_df = pd.read_csv("data/tools/versions/{parent-id}/v{N}/data.csv")
```

### 2. Apply Filters

```python
def apply_split_filter(df, split_filter):
    """Apply split filter to create filtered dataset."""
    result = df.copy()

    for column, value in split_filter.items():
        if value == "latest":
            # Keep only the maximum year
            max_year = result[column].max()
            result = result[result[column] == max_year]
        elif isinstance(value, str) and value.startswith("NOT "):
            # Exclude specific value
            exclude_value = value[4:]
            result = result[result[column] != exclude_value]
        elif isinstance(value, list):
            # Keep rows matching any value in list
            result = result[result[column].isin(value)]
        else:
            # Exact match
            result = result[result[column] == value]

    return result

filtered_df = apply_split_filter(parent_df, split_filter)
```

### 3. Clean and Rename Columns

```python
def clean_for_export(df, split_id):
    """Clean dataframe for export."""
    # Remove filtered columns that have single values
    # (they're now redundant)
    for col in df.columns:
        if df[col].nunique() == 1:
            df = df.drop(columns=[col])

    # Rename columns to user-friendly names
    column_mapping = {
        "Variable": "value",
        "Хүйс": "sex",
        "Насны бүлэг": "age_group",
        # Add more mappings as needed
    }
    df = df.rename(columns=column_mapping)

    return df
```

### 4. Export to CSV (Long Form) and XLSX (Wide Form)

**CRITICAL**: CSV and XLSX have different formats!

```python
def export_dataset(df, dataset_id, lang, time_col='date', category_col=None, value_col='price'):
    """
    Export dataset to CSV (long form) and XLSX (wide form).

    Args:
        df: DataFrame with all data (not chart subset)
        dataset_id: e.g., "weekly-beef-prices"
        lang: "en" or "mn"
        time_col: Column containing time values (date, year, etc.)
        category_col: Column to pivot for XLSX (e.g., "region"). None for simple time series.
        value_col: Column containing numeric values
    """
    output_dir = "data/data.mn/public/datasets"

    # CSV: Long/tidy form - keep as-is
    csv_path = f"{output_dir}/{dataset_id}-{lang}.csv"
    df.to_csv(csv_path, index=False)

    # XLSX: Wide/pivot form - pivot if category_col exists
    xlsx_path = f"{output_dir}/{dataset_id}.xlsx"  # Note: no lang suffix for Excel

    if category_col and category_col in df.columns:
        # Pivot: rows=time, columns=categories, values=value
        wide_df = df.pivot_table(
            index=time_col,
            columns=category_col,
            values=value_col,
            aggfunc='first'  # Should be unique anyway
        ).reset_index()

        # Flatten column names if multi-level
        if hasattr(wide_df.columns, 'levels'):
            wide_df.columns = [str(c) if c else time_col for c in wide_df.columns]
    else:
        # No pivot needed - simple time series
        wide_df = df.copy()

    # Export XLSX with formatting
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        wide_df.to_excel(writer, index=False, sheet_name='Data')

        # Auto-adjust column widths
        worksheet = writer.sheets['Data']
        for idx, col in enumerate(wide_df.columns):
            max_length = max(
                wide_df[col].astype(str).map(len).max(),
                len(str(col))
            ) + 2
            # Handle column index > 26 (Excel column letters)
            col_letter = get_column_letter(idx + 1)
            worksheet.column_dimensions[col_letter].width = min(max_length, 30)

    return csv_path, xlsx_path


def get_column_letter(col_idx):
    """Convert 1-based column index to Excel column letter(s)."""
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result
```

### 5. Export Chart Data (Subset Only)

The chart needs a separate CSV with only the subset of categories:

```python
def export_chart_data(df, dataset_id, lang, chart_subset=None):
    """
    Export chart-specific CSV with subset of data for visualization.

    Args:
        df: Full DataFrame
        chart_subset: dict with "column" and "values" keys
    """
    output_dir = "data/data.mn/public/datasets"

    if chart_subset:
        col = chart_subset["column"]
        values = chart_subset["values"]
        chart_df = df[df[col].isin(values)].copy()
    else:
        chart_df = df.copy()

    # Chart CSV is what the Vega-Lite spec references
    chart_csv_path = f"{output_dir}/{dataset_id}-{lang}.csv"
    chart_df.to_csv(chart_csv_path, index=False)

    return chart_csv_path
```

**Wait!** There's a conflict here. Let me clarify the file naming:

### File Naming Convention (UPDATED)

| File | Contains | Used By |
|------|----------|---------|
| `{id}-{lang}.csv` | **Chart subset** (long form) | Vega-Lite chart spec |
| `{id}-all-{lang}.csv` | **ALL data** (long form) | Download link, PowerBI users |
| `{id}.xlsx` | **ALL data** (wide form) | Download link, Excel users |

```python
def export_all_files(df, dataset_id, lang, time_col, category_col, value_col, chart_subset=None):
    """Export all three file types for a dataset."""
    output_dir = "data/data.mn/public/datasets"

    # 1. Chart CSV (subset, long form) - for Vega-Lite
    if chart_subset:
        chart_df = df[df[chart_subset["column"]].isin(chart_subset["values"])].copy()
    else:
        chart_df = df.copy()
    chart_csv = f"{output_dir}/{dataset_id}-{lang}.csv"
    chart_df.to_csv(chart_csv, index=False)

    # 2. Full CSV (all data, long form) - for technical download
    full_csv = f"{output_dir}/{dataset_id}-all-{lang}.csv"
    df.to_csv(full_csv, index=False)

    # 3. XLSX (all data, wide form) - for Excel download
    xlsx_path = f"{output_dir}/{dataset_id}.xlsx"
    if category_col:
        wide_df = df.pivot_table(
            index=time_col, columns=category_col, values=value_col, aggfunc='first'
        ).reset_index()
    else:
        wide_df = df

    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        wide_df.to_excel(writer, index=False, sheet_name='Data')
        auto_adjust_columns(writer.sheets['Data'], wide_df)

    return {"chart_csv": chart_csv, "full_csv": full_csv, "xlsx": xlsx_path}
```

## Complete Example: Regional Price Data

```python
import pandas as pd

# Define split with chart subset (only 4 regions shown in chart)
split_config = {
    "id": "weekly-beef-prices",
    "parent_id": "nso-weekly-prices-main-products",
    "title_en": "Weekly Beef Prices by Region in Mongolia (2024-2025)",
    "title_mn": "Монгол Улсын бүс нутгаар үхрийн махны долоо хоногийн үнэ (2024-2025)",
    "category_en": "Economy",
    "category_mn": "Эдийн засаг",
    "filter": {"Products": "Beef, kg"},  # Filter to just beef
    # Chart shows 4 representative regions; files contain ALL 25 regions
    "chart_subset": {
        "column": "region",
        "values": ["Ulaanbaatar", "Darkhan-Uul", "Khovd", "Umnugovi"]
    }
}

# Load parent data (contains all products, all regions)
parent_en = pd.read_csv("data/tools/versions/nso-weekly-prices-main-products/nso-0300-010v5-en.csv")
parent_mn = pd.read_csv("data/tools/versions/nso-weekly-prices-main-products/nso-0300-010v5-mn.csv")

# Apply product filter (beef only)
beef_en = parent_en[parent_en["Products"] == "Beef, kg"].copy()
beef_mn = parent_mn[parent_mn["Products"] == "Үхрийн мах, кг"].copy()

# Clean: rename columns, drop product column (now redundant)
beef_en = beef_en.rename(columns={"Time": "date", "Region": "region", "value": "price"})
beef_en = beef_en.drop(columns=["Products"])

beef_mn = beef_mn.rename(columns={"Time": "date", "Region": "region", "value": "price"})
beef_mn = beef_mn.drop(columns=["Products"])

# Export all file types for each language
for lang, df in [("en", beef_en), ("mn", beef_mn)]:
    files = export_all_files(
        df=df,
        dataset_id="weekly-beef-prices",
        lang=lang,
        time_col="date",
        category_col="region",
        value_col="price",
        chart_subset=split_config["chart_subset"]
    )
    print(f"Exported ({lang}):")
    print(f"  Chart CSV (4 regions): {files['chart_csv']}")
    print(f"  Full CSV (25 regions): {files['full_csv']}")
    print(f"  XLSX (wide format):    {files['xlsx']}")
```

### Output:
```
Exported (en):
  Chart CSV (4 regions): weekly-beef-prices-en.csv       # 400 rows (4 regions × 100 weeks)
  Full CSV (25 regions): weekly-beef-prices-all-en.csv   # 2500 rows (25 regions × 100 weeks)
  XLSX (wide format):    weekly-beef-prices.xlsx          # 100 rows × 26 columns

Exported (mn):
  Chart CSV (4 regions): weekly-beef-prices-mn.csv
  Full CSV (25 regions): weekly-beef-prices-all-mn.csv
  XLSX (wide format):    (same file, just one Excel per dataset)
```

## Bilingual Category Reference

When creating split configs, use these bilingual categories:

| English | Mongolian |
|---------|-----------|
| Demographics | Хүн ам зүй |
| Economy | Эдийн засаг |
| Employment | Хөдөлмөр эрхлэлт |
| Housing | Орон сууц |
| Mining | Уул уурхай |
| Finance | Санхүү |
| Agriculture | Хөдөө аж ахуй |
| Education | Боловсрол |
| Health | Эрүүл мэнд |
| Trade | Худалдаа |
| Energy | Эрчим хүч |
| Tourism | Аялал жуулчлал |

## Data Validation

Before exporting, validate the filtered data:

```python
def validate_split(df, split_config):
    """Validate split data before export."""
    errors = []

    # Check not empty
    if len(df) == 0:
        errors.append("Split resulted in empty dataset")

    # Check expected columns exist
    required_columns = ["year", "value"]
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    # Check no null values in key columns
    for col in required_columns:
        if col in df.columns and df[col].isnull().any():
            errors.append(f"Null values found in column: {col}")

    # Check value column is numeric
    if "value" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["value"]):
            errors.append("Value column is not numeric")

    return errors
```

## Output Locations

| Content | Format | Path | Purpose |
|---------|--------|------|---------|
| Chart CSV | Long form, subset | `{id}-{lang}.csv` | Vega-Lite chart data source |
| Download CSV | Long form, ALL data | `{id}-all-{lang}.csv` | Technical users, PowerBI, Tableau |
| Download XLSX | Wide form, ALL data | `{id}.xlsx` | Excel users (one file for both languages) |

**Directory**: `data/data.mn/public/datasets/`

### MDX dataFiles Configuration

In the MDX frontmatter, reference the download files (not chart files):

```yaml
dataFiles:
  - label: "CSV (All Regions)"
    url: "/datasets/weekly-beef-prices-all-en.csv"
  - label: "Excel"
    url: "/datasets/weekly-beef-prices.xlsx"
```

The chart component references its own CSV via the chart JSON spec, not through dataFiles.

## Calculating Statistics

After filtering, calculate key statistics for the excerpt:

```python
def calculate_stats(df):
    """Calculate key statistics for excerpt."""
    stats = {}

    if "year" in df.columns and "value" in df.columns:
        # Time series stats
        stats["first_year"] = df["year"].min()
        stats["last_year"] = df["year"].max()
        stats["first_value"] = df[df["year"] == stats["first_year"]]["value"].iloc[0]
        stats["last_value"] = df[df["year"] == stats["last_year"]]["value"].iloc[0]
        stats["growth_factor"] = stats["last_value"] / stats["first_value"]
        stats["growth_pct"] = (stats["growth_factor"] - 1) * 100

    if "value" in df.columns:
        stats["min"] = df["value"].min()
        stats["max"] = df["value"].max()
        stats["mean"] = df["value"].mean()

    stats["row_count"] = len(df)

    return stats
```

## Notes

- Always validate before exporting
- Keep column names consistent across splits
- Use lowercase, underscore-separated column names
- Include year column for time series data
- The value column should always be numeric
